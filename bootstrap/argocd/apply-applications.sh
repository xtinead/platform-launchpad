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

GITOPS_REPO="${GITOPS_REPO:-/c/apps/platform-launchpad-gitops}"

require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Required command not found: ${command_name}" >&2
    exit 1
  fi
}

for command_name in \
  kubectl \
  git
do
  require_command "${command_name}"
done

if [ ! -d "${GITOPS_REPO}/.git" ]; then
  echo "GitOps repository not found: ${GITOPS_REPO}" >&2
  exit 1
fi

echo "=== Validating GitOps repository ==="

git -C "${GITOPS_REPO}" status --short

echo
echo "=== Waiting for Argo CD CRDs ==="

kubectl wait \
  --for=condition=Established \
  crd/applications.argoproj.io \
  --timeout=120s

kubectl wait \
  --for=condition=Established \
  crd/appprojects.argoproj.io \
  --timeout=120s

echo
echo "=== Applying Argo CD Applications ==="

kubectl apply \
  -f "${GITOPS_REPO}/applications/aws-load-balancer-controller-development.yaml"

kubectl apply \
  -f "${GITOPS_REPO}/applications/development.yaml"

echo
echo "=== Verifying Applications ==="

kubectl get applications \
  -n argocd

echo
echo "Argo CD application bootstrap completed successfully."