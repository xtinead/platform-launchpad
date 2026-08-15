# Platform Launchpad Terraform Bootstrap

The Terraform bootstrap layer creates the shared infrastructure required to
support remote Terraform state for Platform Launchpad.

This layer is intentionally isolated from the main application infrastructure
because Terraform backend resources must exist before environment
configurations can use them.

## Purpose

The bootstrap configuration provisions:

- Amazon S3 bucket for Terraform remote state
- S3 bucket versioning
- Server-side encryption
- S3 public-access protection
- Amazon DynamoDB table for Terraform state locking
- Standard project tags

The bootstrap layer does not provision:

- VPC infrastructure
- Amazon EKS
- Amazon RDS
- Amazon ECR repositories
- Application workloads
- DNS records
- Runtime Kubernetes resources

Those resources are managed by the environment-specific Terraform
configurations.

## Architecture

```text
Terraform Bootstrap
        |
        +-- Amazon S3
        |      |
        |      +-- Remote Terraform state
        |      +-- Versioning
        |      +-- Encryption
        |      +-- Public access blocked
        |
        +-- Amazon DynamoDB
               |
               +-- Terraform state locking