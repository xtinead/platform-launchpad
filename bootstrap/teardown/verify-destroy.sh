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

AWS_REGION="${AWS_REGION:-us-east-1}"
PROJECT_NAME="${PROJECT_NAME:-platform-launchpad}"
ENVIRONMENT="${ENVIRONMENT:-development}"
NAME_PREFIX="${PROJECT_NAME}-${ENVIRONMENT}"

FAILED=0

check_empty() {
  local description="$1"
  local value="$2"

  if [ -n "${value}" ] && [ "${value}" != "None" ]; then
    echo "FAIL: ${description}: ${value}"
    FAILED=1
  else
    echo "PASS: ${description}"
  fi
}

echo "=== Terraform state ==="

STATE_COUNT="$(
  terraform \
    -chdir="${ENVIRONMENT_DIR}" \
    state list \
  | wc -l
)"

if [ "${STATE_COUNT}" -eq 0 ]; then
  echo "PASS: Terraform state is empty."
else
  echo "FAIL: Terraform still tracks ${STATE_COUNT} resource(s)."
  terraform \
    -chdir="${ENVIRONMENT_DIR}" \
    state list
  FAILED=1
fi

echo
echo "=== EKS ==="

EKS_MATCH="$(
  aws eks list-clusters \
    --region "${AWS_REGION}" \
    --query "clusters[?@=='${NAME_PREFIX}-eks']" \
    --output text
)"

check_empty \
  "Platform Launchpad EKS cluster absent" \
  "${EKS_MATCH}"

echo
echo "=== VPC ==="

VPC_MATCH="$(
  aws ec2 describe-vpcs \
    --region "${AWS_REGION}" \
    --filters \
      "Name=tag:Project,Values=${PROJECT_NAME}" \
      "Name=tag:Environment,Values=${ENVIRONMENT}" \
    --query 'Vpcs[].VpcId' \
    --output text
)"

check_empty \
  "Platform Launchpad VPC absent" \
  "${VPC_MATCH}"

echo
echo "=== NAT Gateways ==="

NAT_MATCH="$(
  aws ec2 describe-nat-gateways \
    --region "${AWS_REGION}" \
    --filter \
      Name=state,Values=available,pending \
    --query \
      "NatGateways[?Tags[?Key=='Project' && Value=='${PROJECT_NAME}'] && Tags[?Key=='Environment' && Value=='${ENVIRONMENT}']].NatGatewayId" \
    --output text
)"

check_empty \
  "Platform Launchpad NAT Gateways absent" \
  "${NAT_MATCH}"

echo
echo "=== RDS ==="

RDS_MATCH="$(
  aws rds describe-db-instances \
    --region "${AWS_REGION}" \
    --query \
      "DBInstances[?starts_with(DBInstanceIdentifier, '${NAME_PREFIX}')].DBInstanceIdentifier" \
    --output text
)"

check_empty \
  "Platform Launchpad RDS instances absent" \
  "${RDS_MATCH}"

echo
echo "=== ElastiCache ==="

REDIS_MATCH="$(
  aws elasticache describe-replication-groups \
    --region "${AWS_REGION}" \
    --query \
      "ReplicationGroups[?starts_with(ReplicationGroupId, '${NAME_PREFIX}')].ReplicationGroupId" \
    --output text
)"

check_empty \
  "Platform Launchpad Redis absent" \
  "${REDIS_MATCH}"

echo
echo "=== ECR ==="

for repository in \
  "${NAME_PREFIX}-application" \
  "${NAME_PREFIX}-aws-load-balancer-controller" \
  "${NAME_PREFIX}-argocd" \
  "${NAME_PREFIX}-argocd-dex" \
  "${NAME_PREFIX}-argocd-redis"
do
  if aws ecr describe-repositories \
    --region "${AWS_REGION}" \
    --repository-names "${repository}" \
    >/dev/null 2>&1
  then
    echo "FAIL: ECR repository still exists: ${repository}"
    FAILED=1
  else
    echo "PASS: ECR repository absent: ${repository}"
  fi
done

echo
echo "=== Jenkins IAM user ==="

if aws iam get-user \
  --user-name "${NAME_PREFIX}-jenkins" \
  >/dev/null 2>&1
then
  echo "FAIL: Jenkins IAM user still exists."
  FAILED=1
else
  echo "PASS: Jenkins IAM user absent."
fi

echo
if [ "${FAILED}" -ne 0 ]; then
  echo "Destroy verification FAILED." >&2
  exit 1
fi

echo "Destroy verification PASSED."
