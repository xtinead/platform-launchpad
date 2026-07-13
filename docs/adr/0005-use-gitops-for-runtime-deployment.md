# ADR-0005: Use GitOps for Runtime Deployment

## Status

Accepted

## Context

Platform Launchpad will run production-style workloads on Kubernetes.

The project requires:

- Auditable deployments
- Declarative desired state
- Environment-specific configuration
- Controlled promotion
- Reliable rollback
- Separation between CI and cluster administration
- Clear source-to-runtime traceability

Direct deployment commands from Jenkins would couple the CI system to the cluster and require deployment credentials in the build platform.

## Decision

Platform Launchpad will use GitOps for Kubernetes runtime deployment.

A dedicated GitOps repository will contain:

- Base Kubernetes manifests
- Environment overlays
- Image digests
- ConfigMaps
- Ingress definitions
- Argo CD Application definitions

Jenkins will update approved desired state in the GitOps repository after validation, testing, scanning, and image publication.

Argo CD will continuously reconcile the approved Git state into Amazon EKS.

Rollback will be performed by:

- Reverting the GitOps commit, or
- Creating a corrective commit that restores a known-good image digest

Manual cluster changes are considered drift and should be reconciled back into Git.

## Alternatives Considered

### Jenkins Directly Runs `kubectl`

Rejected because Jenkins would require cluster deployment credentials and would become both the CI system and runtime deployment authority.

### Helm Deployment Directly from Jenkins

This improves packaging but still gives the CI system direct cluster deployment responsibility.

### AWS CodePipeline and CodeDeploy

These AWS-native services could handle delivery, but they would reduce alignment with the existing Jenkins and Argo CD portfolio strategy.

### Manual Kubernetes Deployment

Rejected because it is not reproducible, auditable, or suitable for controlled environment promotion.

### Terraform Manages Application Workloads

Terraform is appropriate for infrastructure but is less suitable as the primary continuous reconciliation mechanism for frequently changing application releases.

## Consequences

### Positive

- Git provides an auditable deployment history.
- Runtime desired state is declarative.
- Argo CD detects and reconciles drift.
- Jenkins does not need broad Kubernetes credentials.
- Rollback uses known Git history.
- Environment overlays support controlled promotion.
- Delivery responsibilities are clearly separated.

### Negative

- A separate GitOps repository must be maintained.
- There can be a delay between Git update and runtime reconciliation.
- Operators must understand both CI and GitOps systems.
- Secret management requires an external mechanism.
- Emergency manual changes require careful reconciliation.

## Review Conditions

Review this decision when:

- The runtime moves away from Kubernetes.
- A managed platform provides equivalent declarative reconciliation.
- GitOps repository management becomes operationally excessive.
- The organization adopts a different standardized deployment controller.
