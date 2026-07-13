# ADR-0007: Use a Monorepo for Initial Development

## Status

Accepted

## Context

Platform Launchpad initially includes several closely related components:

- Next.js frontend
- FastAPI backend
- Python worker
- Docker Compose configuration
- Jenkins pipeline definitions
- Terraform infrastructure code
- Kubernetes and GitOps configuration
- Product and architecture documentation

The project could begin as multiple repositories, with separate repositories for application code, infrastructure, GitOps, observability, and documentation.

However, the application architecture, interfaces, release process, and ownership boundaries are still evolving. Splitting the project into many repositories at the beginning would introduce additional operational overhead, including:

- Cross-repository version coordination
- Multiple CI pipelines
- More repository administration
- More complex local development
- Additional pull requests for one logical change
- Increased documentation synchronization
- More complex dependency management
- More difficult end-to-end testing

Platform Launchpad is initially maintained by one engineer and must remain practical to build, test, document, and demonstrate.

The repository strategy should support rapid development now without preventing stronger separation later.

---

## Decision

Platform Launchpad will begin as a monorepo.

The initial repository structure will be:

```text
platform-launchpad/
├── frontend/
├── backend/
├── worker/
├── docker/
├── deploy/
├── terraform/
├── jenkins/
├── docs/
├── docker-compose.yml
├── .gitignore
└── README.md
```

The monorepo will contain:

- Frontend application source
- Backend API source
- Worker source
- Local Docker configuration
- CI/CD pipeline definitions
- Terraform infrastructure code
- Deployment configuration
- Architecture documentation
- Tests
- Developer setup instructions

Logical separation will still be maintained through:

- Clear directory boundaries
- Independent service Dockerfiles
- Independent dependency manifests
- Independent test suites
- Service-specific pipeline stages
- Well-defined API contracts
- Documented ownership and responsibilities

The application source repository will not become the Kubernetes runtime source of truth.

A separate GitOps repository may be introduced earlier than the other repository splits because it has a distinct responsibility:

- It defines desired Kubernetes runtime state.
- It is reconciled by Argo CD.
- It has different access-control requirements.
- It supports independent environment promotion and rollback.

A future repository split may create dedicated repositories such as:

```text
platform-launchpad-app
platform-launchpad-infrastructure
platform-launchpad-gitops
platform-launchpad-observability
platform-launchpad-docs
platform-launchpad-ci-cd
```

The repository should be split only when the operational or ownership benefits clearly outweigh the coordination cost.

---

## Alternatives Considered

### Multiple Repositories from the Beginning

The project could begin with separate repositories for:

- Application code
- Infrastructure
- GitOps
- CI/CD
- Observability
- Documentation

This approach would provide stronger separation of concerns and independent access controls.

It was not selected initially because it would introduce significant coordination overhead before the project boundaries and workflows are stable.

### One Repository per Application Service

The frontend, backend, and worker could each have a separate repository.

This would support independent versioning and deployments.

It was rejected because the services are closely related, share one product lifecycle, and are initially maintained by one engineer. Many changes will require coordinated updates across the API, frontend, worker, tests, and documentation.

### Store Everything in the GitOps Repository

Application source, infrastructure, and runtime manifests could be stored in one GitOps-oriented repository.

This was rejected because application source and runtime desired state have different responsibilities, deployment workflows, and security boundaries.

The GitOps repository should contain approved runtime configuration rather than source code and build logic.

### Separate Infrastructure Repository Only

Terraform could be moved into its own repository from the beginning.

This would improve infrastructure access control and isolate Terraform pipelines.

It remains a valid future option, but the infrastructure design is still evolving and benefits from being developed alongside the application during the initial phase.

### Separate Documentation Repository

Architecture and product documentation could be maintained independently.

This was rejected because documentation should evolve in the same pull request as the implementation and design changes it describes.

---

## Consequences

### Positive

- Initial development is faster.
- Local setup is simpler.
- One clone contains the complete project.
- One pull request can update the API, frontend, worker, tests, infrastructure, and documentation together.
- Cross-component changes can be committed atomically.
- End-to-end testing is easier to coordinate.
- Repository administration remains lightweight.
- Architecture documentation stays close to implementation.
- The project is easier to demonstrate during interviews.
- Service and repository boundaries can be refined based on real implementation experience.

### Negative

- Repository size will grow over time.
- CI pipelines may become slower unless path-based execution is introduced.
- Access-control boundaries are weaker than in separate repositories.
- Git history contains changes from multiple engineering domains.
- Infrastructure and application code share the same repository permissions initially.
- Independent service releases may become harder as the project grows.
- A future repository split may require migration work.
- `CODEOWNERS` and path-based review rules may be needed as sensitive areas grow.

---

## Implementation Guidance

The monorepo should use clear boundaries from the beginning.

### Service Boundaries

Each service should maintain its own:

- Dependency manifest
- Dockerfile
- Tests
- Configuration
- README
- Build commands

### CI Optimization

Jenkins pipelines should eventually detect changed paths and run only the required stages.

Examples:

```text
backend/**   → Backend validation and build
frontend/**  → Frontend validation and build
worker/**    → Worker validation and build
terraform/** → Terraform validation and plan
docs/**      → Documentation validation
```

Full integration pipelines should still run for release candidates.

### Security Boundaries

Sensitive paths should receive additional review.

Examples:

```text
backend/app/core/security/**
jenkins/**
terraform/**
deploy/**
docs/security/**
```

A future `CODEOWNERS` file may enforce review requirements for these paths.

### Repository Split Triggers

A repository split should be considered when one or more of the following become true:

- Components require independent release cycles.
- Different teams own different components.
- CI duration becomes excessive.
- Infrastructure requires stricter permissions.
- GitOps access must be separated from application-development access.
- Shared Jenkins libraries become reusable across projects.
- Terraform modules are reused by multiple platforms.
- Documentation requires an independent publishing lifecycle.
- Repository size significantly affects developer workflows.

---

## Consequences for CI/CD

The monorepo CI/CD design must:

- Support service-specific validation.
- Avoid unnecessary builds where practical.
- Preserve one end-to-end integration pipeline.
- Build separate frontend, backend, and worker images.
- Publish independent image digests.
- Track which services changed.
- Update only affected GitOps image references.
- Maintain one release record that can reference multiple service artifacts.

---

## Consequences for Versioning

The project may initially use one product release version while publishing separate service images.

Example:

```text
Platform Launchpad release: 1.0.0

Frontend image:
platform-launchpad-frontend:1.0.0

Backend image:
platform-launchpad-backend:1.0.0

Worker image:
platform-launchpad-worker:1.0.0
```

If independent service release cycles become necessary, the repository strategy and versioning model should be reviewed.

---

## Review Conditions

Review this decision when:

- Frontend, backend, or worker services require independent release cycles.
- Different teams or owners manage different components.
- Repository CI time becomes excessive.
- Infrastructure permissions require stronger repository isolation.
- GitOps security requires independent repository access.
- Terraform modules are reused outside Platform Launchpad.
- Shared Jenkins libraries emerge.
- The repository becomes difficult to navigate or maintain.
- A split would improve ownership without creating excessive coordination overhead.