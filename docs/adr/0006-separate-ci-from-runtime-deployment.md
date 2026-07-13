# ADR-0006: Separate Continuous Integration from Runtime Deployment

## Status

Accepted

## Context

Jenkins is the selected Continuous Integration platform.

The application also requires controlled deployment to Kubernetes through Argo CD.

Allowing Jenkins to build, publish, and deploy directly would require the CI system to hold powerful runtime credentials and would blur responsibility between artifact production and environment reconciliation.

The platform requires a design that limits blast radius and provides clear auditability.

## Decision

Jenkins and Argo CD will have separate responsibilities.

Jenkins will:

- Check out source code
- Validate formatting and linting
- Run tests
- Validate the OpenAPI contract
- Run security scans
- Build container images
- Scan container images
- Push approved images to Amazon ECR
- Capture immutable image digests
- Update the GitOps repository
- Publish pipeline notifications

Argo CD will:

- Read approved GitOps repositories
- Compare desired state with cluster state
- Reconcile approved changes
- Report synchronization and health status

Jenkins will not receive unrestricted cluster-admin credentials and will not perform normal workload deployments with direct `kubectl` commands.

Terraform infrastructure delivery will use a separate, controlled Jenkins role and pipeline.

## Alternatives Considered

### One Jenkins Pipeline Performs Everything

Rejected because it creates excessive privilege concentration and a larger CI compromise blast radius.

### Argo CD Builds Images

Rejected because Argo CD is a deployment reconciler, not a CI or artifact-build platform.

### Use Only GitHub Actions

GitHub Actions could perform CI, but Jenkins is an important skill in the user's portfolio and existing environment.

### Manual Promotion

Rejected because it weakens repeatability and delivery traceability.

## Consequences

### Positive

- Jenkins requires fewer runtime privileges.
- Argo CD remains the deployment authority.
- CI failures and runtime failures are easier to distinguish.
- GitOps history connects artifact promotion to runtime state.
- Security boundaries are easier to explain and test.
- A compromised build job has reduced direct cluster access.

### Negative

- Delivery spans multiple systems.
- Troubleshooting requires correlation between Jenkins, Git, Argo CD, and Kubernetes.
- GitOps update conflicts must be handled.
- Post-deployment verification requires integration across tools.

## Review Conditions

Review this decision when:

- The organization adopts a different CI platform.
- Kubernetes is no longer the runtime.
- A unified platform provides equivalent security separation.
- GitOps update complexity becomes disproportionate to project needs.
