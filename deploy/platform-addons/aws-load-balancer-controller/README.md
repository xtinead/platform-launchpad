# AWS Load Balancer Controller

This directory contains the version-controlled Helm configuration for the
AWS Load Balancer Controller used by the Platform Launchpad development EKS
cluster.

## Architecture

The controller runs in the `kube-system` namespace and manages AWS Application
Load Balancers for Kubernetes Ingress resources.

The controller uses:

- AWS Load Balancer Controller v3.5.0
- Helm chart 3.5.0
- EKS Pod Identity
- A dedicated IAM role and IAM policy managed by Terraform
- A private Amazon ECR repository
- An Elastic Load Balancing VPC interface endpoint
- Private EKS worker nodes without general internet egress

The controller image is mirrored from public ECR into the Platform Launchpad
private ECR registry so worker nodes do not require internet access to pull it.

## Prerequisites

The following infrastructure must already exist:

- EKS cluster
- EKS managed node group
- EKS Pod Identity Agent
- EKS Auth VPC endpoint
- Elastic Load Balancing VPC endpoint
- ECR API and ECR Docker VPC endpoints
- S3 gateway endpoint
- AWS Load Balancer Controller IAM policy
- AWS Load Balancer Controller Pod Identity IAM role
- EKS Pod Identity association

Terraform manages these prerequisites.

## Install or Upgrade

From the repository root:

```bash
helm upgrade --install aws-load-balancer-controller \
  eks/aws-load-balancer-controller \
  --namespace kube-system \
  --version 3.5.0 \
  --values deploy/platform-addons/aws-load-balancer-controller/values.yaml \
  --wait \
  --timeout 10m