#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(
  cd "$(dirname "${BASH_SOURCE[0]}")" &&
    pwd
)"

REPO_ROOT="$(
  cd "${SCRIPT_DIR}/../.." &&
    pwd
)"

ENVIRONMENT_DIR="${REPO_ROOT}/terraform/environments/development"

APPLICATION_NAME="platform-launchpad-development"
CONTROLLER_APPLICATION_NAME="aws-load-balancer-controller-development"
APPLICATION_NAMESPACE="platform-launchpad"
ARGOCD_NAMESPACE="argocd"

require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Required command not found: ${command_name}" >&2
    exit 1
  fi
}

application_exists() {
  kubectl get application \
    "$1" \
    -n "${ARGOCD_NAMESPACE}" \
    >/dev/null 2>&1
}

cascade_delete_application() {
  local application_name="$1"

  if ! application_exists "${application_name}"; then
    echo "Application already absent: ${application_name}"
    return
  fi

  echo "Adding Argo CD resource finalizer: ${application_name}"

  kubectl patch application \
    "${application_name}" \
    -n "${ARGOCD_NAMESPACE}" \
    --type merge \
    -p '{
      "metadata": {
        "finalizers": [
          "resources-finalizer.argocd.argoproj.io"
        ]
      }
    }'

  echo "Deleting Argo CD Application: ${application_name}"

  kubectl delete application \
    "${application_name}" \
    -n "${ARGOCD_NAMESPACE}"

  kubectl wait \
    --for=delete \
    "application/${application_name}" \
    -n "${ARGOCD_NAMESPACE}" \
    --timeout=300s
}

echo "=== Validating prerequisites ==="

for command_name in \
  aws \
  kubectl \
  terraform
do
  require_command "${command_name}"
done

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

echo
echo "=== AWS identity ==="

aws sts get-caller-identity \
  --query '{Account:Account,Arn:Arn}' \
  --output table

echo
echo "=== Updating kubeconfig ==="

aws eks update-kubeconfig \
  --region "${AWS_REGION}" \
  --name "${CLUSTER_NAME}"

echo
echo "=== Disabling application auto-reconciliation ==="

for application_name in \
  "${APPLICATION_NAME}" \
  "${CONTROLLER_APPLICATION_NAME}"
do
  if application_exists "${application_name}"; then
    kubectl patch application \
      "${application_name}" \
      -n "${ARGOCD_NAMESPACE}" \
      --type merge \
      -p '{"spec":{"syncPolicy":{"automated":null}}}'
  fi
done

echo
echo "=== Capturing application ALB hostname ==="

ALB_DNS="$(
  kubectl get ingress \
    -n "${APPLICATION_NAMESPACE}" \
    platform-launchpad \
    -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' \
    2>/dev/null \
    || true
)"

if [ -n "${ALB_DNS}" ]; then
  echo "Application ALB: ${ALB_DNS}"
else
  echo "Application Ingress or ALB already absent."
fi

echo
echo "=== Removing application Ingress ==="

kubectl delete ingress \
  platform-launchpad \
  -n "${APPLICATION_NAMESPACE}" \
  --ignore-not-found=true

if [ -n "${ALB_DNS}" ]; then
  echo
  echo "=== Waiting for AWS Load Balancer deletion ==="

  for attempt in $(seq 1 60); do
    MATCH="$(
      aws elbv2 describe-load-balancers \
        --region "${AWS_REGION}" \
        --query "LoadBalancers[?DNSName=='${ALB_DNS}'].DNSName" \
        --output text
    )"

    if [ -z "${MATCH}" ]; then
      echo "Application ALB deleted."
      break
    fi

    if [ "${attempt}" -eq 60 ]; then
      echo "Timed out waiting for application ALB deletion." >&2
      exit 1
    fi

    sleep 10
  done
fi

echo
echo "=== Removing application runtime through Argo CD ==="

cascade_delete_application \
  "${APPLICATION_NAME}"

echo
echo "=== Removing AWS Load Balancer Controller through Argo CD ==="

cascade_delete_application \
  "${CONTROLLER_APPLICATION_NAME}"

echo
echo "=== Confirming no Platform Launchpad Kubernetes applications remain ==="

kubectl get applications \
  -n "${ARGOCD_NAMESPACE}" \
  || true

echo
echo "Pre-destroy cleanup completed."
echo
echo "Next:"
echo "  terraform -chdir=${ENVIRONMENT_DIR} plan -destroy"
