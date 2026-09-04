#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" \
    && pwd
)"

REPO_ROOT="$(
  cd "${SCRIPT_DIR}/../.." \
    && pwd
)"

ENVIRONMENT_DIR="$(
  cd "${REPO_ROOT}/terraform/environments/development" \
    && pwd
)"

source "${SCRIPT_DIR}/images.env"

AWS_REGION="$(
  terraform \
    -chdir="${ENVIRONMENT_DIR}" \
    output -raw aws_region
)"

CLUSTER_NAME="$(
  terraform \
    -chdir="${ENVIRONMENT_DIR}" \
    output -raw eks_cluster_name
)"

ARGOCD_REPOSITORY_URL="$(
  terraform \
    -chdir="${ENVIRONMENT_DIR}" \
    output -json argocd_repository_urls \
  | python -c '
import json
import sys

print(json.load(sys.stdin)["argocd"])
'
)"

DEX_REPOSITORY_URL="$(
  terraform \
    -chdir="${ENVIRONMENT_DIR}" \
    output -json argocd_repository_urls \
  | python -c '
import json
import sys

print(json.load(sys.stdin)["dex"])
'
)"

REDIS_REPOSITORY_URL="$(
  terraform \
    -chdir="${ENVIRONMENT_DIR}" \
    output -json argocd_repository_urls \
  | python -c '
import json
import sys

print(json.load(sys.stdin)["redis"])
'
)"

ARGOCD_PRIVATE_IMAGE="${ARGOCD_REPOSITORY_URL}:${ARGOCD_VERSION}"
DEX_PRIVATE_IMAGE="${DEX_REPOSITORY_URL}:${DEX_VERSION}"
REDIS_PRIVATE_IMAGE="${REDIS_REPOSITORY_URL}:${REDIS_VERSION}"

ARGOCD_REPOSITORY_NAME="${ARGOCD_REPOSITORY_URL#*/}"
DEX_REPOSITORY_NAME="${DEX_REPOSITORY_URL#*/}"
REDIS_REPOSITORY_NAME="${REDIS_REPOSITORY_URL#*/}"

MANIFEST_URL="https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/install.yaml"

WORK_DIR="$(
  mktemp -d
)"

MANIFEST_PATH="${WORK_DIR}/install.yaml"

cleanup() {
  rm -rf "${WORK_DIR}"
}

trap cleanup EXIT

require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Required command not found: ${command_name}" >&2
    exit 1
  fi
}

image_exists() {
  local repository_name="$1"
  local image_tag="$2"

  aws ecr describe-images \
    --repository-name "${repository_name}" \
    --image-ids "imageTag=${image_tag}" \
    --region "${AWS_REGION}" \
    >/dev/null 2>&1
}

mirror_image() {
  local upstream_image="$1"
  local private_image="$2"
  local repository_name="$3"
  local image_tag="$4"

  if image_exists "${repository_name}" "${image_tag}"; then
    echo "Image already present in ECR: ${private_image}"
    return
  fi

  echo "Pulling upstream image: ${upstream_image}"
  docker pull "${upstream_image}"

  echo "Tagging private image: ${private_image}"
  docker tag \
    "${upstream_image}" \
    "${private_image}"

  echo "Pushing private image: ${private_image}"
  docker push "${private_image}"
}

echo "=== Validating prerequisites ==="

for command_name in \
  aws \
  curl \
  docker \
  kubectl \
  terraform \
  python
do
  require_command "${command_name}"
done

echo "All required commands are available."

echo
echo "=== Validating AWS identity ==="

aws sts get-caller-identity \
  --query '{Account:Account,Arn:Arn}' \
  --output table

echo
echo "=== Updating kubeconfig ==="

aws eks update-kubeconfig \
  --region "${AWS_REGION}" \
  --name "${CLUSTER_NAME}"

echo
echo "=== Validating cluster access ==="

kubectl get nodes

echo
echo "=== Authenticating Docker to private ECR ==="

ECR_REGISTRY="$(
  printf '%s\n' "${ARGOCD_REPOSITORY_URL}" \
  | cut -d/ -f1
)"

EXPECTED_ACCOUNT_ID="${ECR_REGISTRY%%.*}"

CURRENT_ACCOUNT_ID="$(
  aws sts get-caller-identity \
    --query Account \
    --output text
)"

if [ "${CURRENT_ACCOUNT_ID}" != "${EXPECTED_ACCOUNT_ID}" ]; then
  echo "AWS account mismatch." >&2
  echo "Expected: ${EXPECTED_ACCOUNT_ID}" >&2
  echo "Current:  ${CURRENT_ACCOUNT_ID}" >&2
  exit 1
fi

echo "AWS account verified: ${CURRENT_ACCOUNT_ID}"

aws ecr get-login-password \
  --region "${AWS_REGION}" \
| docker login \
    --username AWS \
    --password-stdin "${ECR_REGISTRY}"

echo
echo "=== Mirroring Argo CD images ==="

mirror_image \
  "${ARGOCD_UPSTREAM_IMAGE}:${ARGOCD_VERSION}" \
  "${ARGOCD_PRIVATE_IMAGE}" \
  "${ARGOCD_REPOSITORY_NAME}" \
  "${ARGOCD_VERSION}"

mirror_image \
  "${DEX_UPSTREAM_IMAGE}:${DEX_VERSION}" \
  "${DEX_PRIVATE_IMAGE}" \
  "${DEX_REPOSITORY_NAME}" \
  "${DEX_VERSION}"

mirror_image \
  "${REDIS_UPSTREAM_IMAGE}:${REDIS_VERSION}" \
  "${REDIS_PRIVATE_IMAGE}" \
  "${REDIS_REPOSITORY_NAME}" \
  "${REDIS_VERSION}"

echo
echo "=== Downloading pinned Argo CD manifest ==="

curl -fsSL \
  "${MANIFEST_URL}" \
  -o "${MANIFEST_PATH}"

echo
echo "=== Rewriting images to private ECR ==="

python "${SCRIPT_DIR}/rewrite_manifest.py" \
  "${MANIFEST_PATH}" \
  "${ARGOCD_UPSTREAM_IMAGE}:${ARGOCD_VERSION}" \
  "${ARGOCD_PRIVATE_IMAGE}" \
  "${DEX_UPSTREAM_IMAGE}:${DEX_VERSION}" \
  "${DEX_PRIVATE_IMAGE}" \
  "${REDIS_UPSTREAM_IMAGE}:${REDIS_VERSION}" \
  "${REDIS_PRIVATE_IMAGE}"

echo
echo "=== Validating rewritten manifest ==="

if grep -Eq \
  'image:.*(quay\.io|ghcr\.io|public\.ecr\.aws)' \
  "${MANIFEST_PATH}"
then
  echo "Public image reference remains in manifest." >&2
  exit 1
fi

echo "No public runtime image references remain."

echo
echo "=== Ensuring Argo CD namespace exists ==="

kubectl create namespace argocd \
  --dry-run=client \
  -o yaml \
| kubectl apply -f -

echo
echo "=== Installing Argo CD ==="

kubectl apply \
  --server-side \
  --force-conflicts \
  -n argocd \
  -f "${MANIFEST_PATH}"

echo
echo "=== Waiting for Argo CD workloads ==="

for deployment in \
  argocd-server \
  argocd-repo-server \
  argocd-applicationset-controller \
  argocd-dex-server \
  argocd-redis \
  argocd-notifications-controller
do
  kubectl rollout status \
    "deployment/${deployment}" \
    -n argocd \
    --timeout=300s
done

kubectl rollout status \
  statefulset/argocd-application-controller \
  -n argocd \
  --timeout=300s

echo
echo "=== Verifying Argo CD CRDs ==="

kubectl get crd \
  applications.argoproj.io \
  applicationsets.argoproj.io \
  appprojects.argoproj.io

echo
echo "=== Verifying Argo CD runtime images ==="

kubectl get pods \
  -n argocd \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{range .spec.initContainers[*]}  init: {.image}{"\n"}{end}{range .spec.containers[*]}  container: {.image}{"\n"}{end}{"\n"}{end}'

PUBLIC_IMAGE_COUNT="$(
  kubectl get pods \
    -n argocd \
    -o jsonpath='{range .items[*]}{range .spec.initContainers[*]}{.image}{"\n"}{end}{range .spec.containers[*]}{.image}{"\n"}{end}{end}' \
  | grep -Ec \
      '^(quay\.io|ghcr\.io|public\.ecr\.aws)' \
    || true
)"

if [ "${PUBLIC_IMAGE_COUNT}" -ne 0 ]; then
  echo "Argo CD is still using public runtime images." >&2
  exit 1
fi

echo
echo "Argo CD bootstrap completed successfully."