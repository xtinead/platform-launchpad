# ADR-0012: Use Separate Terraform State per Environment

## Status

Accepted

## Context

Platform Launchpad will support development, staging, and production-style environments.

Using one Terraform state file for all environments would tightly couple unrelated resources and increase the blast radius of:

- Terraform plan
- Terraform apply
- Terraform destroy
- State corruption
- Resource replacement
- Operator error

The project needs environment isolation while remaining manageable for a portfolio implementation.

## Decision

Each Platform Launchpad environment will use a separate Terraform state key.

Example:

```text
platform-launchpad/development/terraform.tfstate
platform-launchpad/staging/terraform.tfstate
platform-launchpad/production/terraform.tfstate
```

All environments may initially share the same encrypted S3 state bucket and DynamoDB lock table.

Each environment directory contains its own:

- Backend configuration
- Variable values
- Terraform plan
- Terraform apply workflow
- Destruction workflow

The state backend resources are managed separately through the bootstrap layer.

## Alternatives Considered

### One State File for Every Environment

Rejected because it creates excessive coupling and increases the risk of unintended cross-environment changes.

### Terraform Workspaces Only

Workspaces can separate state, but environment-specific configuration and review can become less explicit.

Workspaces may still be useful in some modules, but they will not be the primary isolation strategy.

### Separate AWS Account and State Bucket per Environment

This provides stronger isolation and is desirable in larger organizations, but it adds excessive cost and administrative complexity for the initial portfolio release.

### Local State

Rejected because it is not suitable for controlled CI/CD, collaboration, or recovery.

## Consequences

### Positive

- Reduced change blast radius
- Safer environment teardown
- Clear environment-specific plans
- Easier CI/CD approvals
- Easier drift detection
- Easier state recovery
- Development changes do not automatically affect production state

### Negative

- Some configuration is repeated across environment directories.
- Shared-resource ownership must be explicit.
- Cross-environment outputs require deliberate integration.
- Multiple state files require consistent naming and access control.

## Review Conditions

Review this decision when:

- Separate AWS accounts are introduced.
- The number of environments grows significantly.
- A Terraform orchestration platform is adopted.
- Environment creation becomes fully dynamic.
- Shared-resource dependencies become difficult to manage.