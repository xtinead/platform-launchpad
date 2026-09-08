#!/usr/bin/env bash

set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
PROJECT_NAME="${PROJECT_NAME:-platform-launchpad}"
ENVIRONMENT="${ENVIRONMENT:-development}"

echo "=== Discovering Platform Launchpad VPC ==="

VPC_ID="$(
  aws ec2 describe-vpcs \
    --region "${AWS_REGION}" \
    --filters \
      "Name=tag:Project,Values=${PROJECT_NAME}" \
      "Name=tag:Environment,Values=${ENVIRONMENT}" \
    --query 'Vpcs[0].VpcId' \
    --output text
)"

if [ -z "${VPC_ID}" ] || [ "${VPC_ID}" = "None" ]; then
  echo "Platform Launchpad VPC already absent."
  exit 0
fi

echo "VPC: ${VPC_ID}"

echo
echo "=== Removing unattached aws-K8S ENIs ==="

ENIS="$(
  aws ec2 describe-network-interfaces \
    --region "${AWS_REGION}" \
    --filters \
      "Name=vpc-id,Values=${VPC_ID}" \
      "Name=status,Values=available" \
    --query \
      'NetworkInterfaces[?RequesterManaged==`false` && starts_with(Description, `aws-K8S-`) && Attachment==null].NetworkInterfaceId' \
    --output text
)"

if [ -z "${ENIS}" ]; then
  echo "No orphaned aws-K8S ENIs found."
else
  for eni in ${ENIS}; do
    echo "Deleting orphaned ENI: ${eni}"

    aws ec2 delete-network-interface \
      --region "${AWS_REGION}" \
      --network-interface-id "${eni}"
  done
fi

echo
echo "=== Removing unused EKS-created cluster security groups ==="

SECURITY_GROUPS="$(
  aws ec2 describe-security-groups \
    --region "${AWS_REGION}" \
    --filters \
      "Name=vpc-id,Values=${VPC_ID}" \
    --query \
      "SecurityGroups[?starts_with(GroupName, \`eks-cluster-sg-${PROJECT_NAME}-${ENVIRONMENT}-eks-\`)].GroupId" \
    --output text
)"

if [ -z "${SECURITY_GROUPS}" ]; then
  echo "No residual EKS cluster security groups found."
else
  for security_group in ${SECURITY_GROUPS}; do
    ENI_COUNT="$(
      aws ec2 describe-network-interfaces \
        --region "${AWS_REGION}" \
        --filters \
          "Name=group-id,Values=${security_group}" \
        --query 'length(NetworkInterfaces)' \
        --output text
    )"

    if [ "${ENI_COUNT}" -ne 0 ]; then
      echo "Skipping ${security_group}; still used by ${ENI_COUNT} ENI(s)."
      continue
    fi

    echo "Deleting residual EKS security group: ${security_group}"

    aws ec2 delete-security-group \
      --region "${AWS_REGION}" \
      --group-id "${security_group}"
  done
fi

echo
echo "Residual EKS cleanup completed."
