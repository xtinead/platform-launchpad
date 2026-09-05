# Platform Launchpad - Technical Design

## 1. Purpose

Platform Launchpad is a production-style internal developer platform portfolio project designed to demonstrate both application engineering and platform engineering practices.

The platform provides a self-service interface through which authenticated users can create and manage logical application environments while backend services coordinate lifecycle state, deployment requests, audit history, and asynchronous processing.

Beyond the application itself, the project demonstrates the supporting platform required to operate it:

- AWS infrastructure provisioned through Terraform
- Amazon EKS as the Kubernetes runtime
- Amazon ECR for private container distribution
- Amazon RDS for PostgreSQL
- AWS Secrets Manager for runtime secrets
- Kubernetes workload identity and AWS access controls
- AWS Load Balancer Controller for ingress
- AWS Certificate Manager for TLS
- Argo CD for GitOps reconciliation
- Jenkins-oriented continuous integration
- immutable image delivery
- automated database migrations
- reproducible platform bootstrap
- teardown and rebuild capability

The authoritative deployed topology is documented in
[`system-architecture.md`](./system-architecture.md).

This document focuses on the technical design, component responsibilities,
engineering boundaries, and how the design evolved during implementation.

---

## 2. Design Goals

Platform Launchpad is designed around the following goals.

### Self-Service

Application users should interact with platform capabilities through a clear
web interface rather than requiring direct access to Kubernetes, AWS, Jenkins,
or Terraform.

### Separation of Responsibilities

Application behavior, continuous integration, infrastructure provisioning,
and runtime deployment should remain separate concerns.

### GitOps Delivery

Runtime Kubernetes state should be declared in Git and reconciled by Argo CD
rather than being deployed directly from the CI system.

### Reproducibility

Infrastructure and platform services should be reconstructable from source
control using Terraform and documented bootstrap automation.

### Security

The design should use:

- least-privilege IAM
- private container repositories
- external secret storage
- Kubernetes service accounts
- encrypted application traffic
- backend-enforced authorization

### Auditability

Important application and deployment operations should leave durable records
that can be inspected later.

### Operational Visibility

The application and platform should expose health, readiness, logs, metrics,
and eventually distributed tracing.

### Cost Control

The AWS environment should be capable of being intentionally destroyed after
validation and reconstructed when needed.

---

## 3. Architectural Principles

Several principles guide the implementation.

### 3.1 Git Is the Runtime Source of Truth

Kubernetes runtime configuration is stored in the GitOps repository.

Argo CD continuously compares desired state in Git with actual state in the
cluster.

Application deployment changes therefore flow through Git rather than direct
imperative deployment commands.

### 3.2 CI Does Not Own the Kubernetes Runtime

Jenkins is responsible for continuous integration activities such as:

- source checkout
- dependency installation
- testing
- static analysis
- security scanning
- container builds
- image publication
- GitOps repository updates

Jenkins does not require direct `kubectl` deployment access to application
workloads.

Argo CD owns runtime reconciliation.

### 3.3 Infrastructure Is Managed as Code

AWS infrastructure is declared through Terraform modules.

The development environment is designed so that:

```text
Terraform configuration
        |
        v
Terraform plan/apply
        |
        v
AWS infrastructure
```

remains reproducible and drift can be detected through `terraform plan`.

### 3.4 Application State and Platform State Are Separate

Application business state is stored in PostgreSQL.

Platform desired state is stored in Terraform and Git.

Kubernetes runtime state is treated as reconstructable rather than as the
authoritative source of configuration.

### 3.5 Runtime Artifacts Are Immutable

Application deployments use immutable container image references.

Container artifacts are published to Amazon ECR and Kubernetes deployments
consume approved immutable versions rather than relying on mutable runtime
state.

---

## 4. Major Components

The implemented architecture consists of:

1. Next.js frontend
2. FastAPI backend
3. PostgreSQL
4. Python deployment worker
5. Amazon EKS
6. Amazon ECR
7. Amazon RDS
8. AWS Secrets Manager
9. Secrets Store CSI Driver
10. AWS Load Balancer Controller
11. Application Load Balancer
12. AWS Certificate Manager
13. Argo CD
14. GitOps repository
15. Terraform
16. Jenkins-oriented CI delivery
17. AWS networking and IAM services
18. observability interfaces

Redis remains represented in the broader platform design and Terraform
structure, but it is not required as the primary queue mechanism for the
currently validated deployment-worker workflow.

---

## 5. Frontend Design

The frontend is implemented using Next.js and TypeScript.

Its responsibilities include:

- authentication user experience
- dashboard presentation
- environment management
- deployment-request submission
- deployment-status presentation
- role-aware navigation
- audit and operational views
- communication with the FastAPI API

The frontend is intentionally prevented from becoming a privileged platform
component.

It does not directly communicate with:

- PostgreSQL
- Kubernetes
- Terraform
- Jenkins
- AWS infrastructure APIs

All privileged application operations pass through the backend authorization
boundary.

---

## 6. Backend API Design

The backend is implemented using FastAPI.

Primary responsibilities include:

- user authentication
- JWT validation
- role-based authorization
- environment management
- deployment-request management
- audit logging
- lifecycle state management
- health endpoints
- readiness endpoints
- operational API endpoints
- persistence through PostgreSQL

The backend remains the primary application authorization boundary.

Frontend authorization checks improve user experience but are not trusted as
security controls.

The deployed backend exposes Kubernetes-compatible health interfaces,
including:

```text
/health/live
/health/ready
```

Readiness validation includes database connectivity.

---

## 7. PostgreSQL Design

PostgreSQL is the system of record for application state.

Persistent records include:

- users
- environments
- deployment requests
- audit events
- application metadata

Local development uses containerized PostgreSQL.

The AWS environment uses Amazon RDS.

Application state is therefore independent from Kubernetes pod lifecycle.

Deleting or recreating application pods does not redefine the authoritative
application state.

---

## 8. Deployment Worker Design

The Python worker performs asynchronous deployment-request processing.

The worker:

- polls for eligible deployment requests
- claims work
- processes lifecycle operations
- updates deployment-request state
- updates environment state
- records outcomes
- handles failures
- emits operational logs

The validated AWS deployment has demonstrated successful worker processing of
deployment requests.

The worker architecture intentionally separates asynchronous lifecycle work
from synchronous API request handling.

This allows the API to accept a deployment request and return without keeping
the HTTP request open for the entire lifecycle operation.

---

## 9. Queue Design Evolution

The original Sprint 0 design assumed Redis would provide the primary
background-task queue.

During implementation, the deployment workflow evolved toward a
database-backed polling model for the current scope.

This reduced operational dependencies while retaining:

- asynchronous processing
- durable request state
- explicit lifecycle status
- retry capability
- auditability

Redis remains available as a future architectural option for workloads that
require higher-throughput messaging, distributed coordination, caching, or
more sophisticated queue semantics.

This change demonstrates an intentional design principle:

> Platform components should be introduced because operational requirements
> justify them, not simply because they appeared in the initial architecture.

---

## 10. Environment Lifecycle

Environment lifecycle state is persisted rather than inferred from ephemeral
worker state.

Representative states include:

```text
pending
provisioning
active
failed
destroying
destroyed
```

A deployment request represents an asynchronous operation against an
environment.

Representative operations include:

```text
provision
upgrade
retry
destroy
```

### Request Flow

```text
User
 |
 v
Next.js
 |
 v
FastAPI
 |
 +---- persist deployment request ----> PostgreSQL
 |
 v
HTTP 202 Accepted

Worker
 |
 +---- claim/process request
 |
 +---- update request state
 |
 +---- update environment state
 |
 v
PostgreSQL
```

This design keeps user-facing API latency independent from longer-running
background operations.

---

## 11. Authentication and Authorization

Authentication uses application-managed credentials and JWT access tokens.

Passwords are:

- hashed before persistence
- excluded from application logs
- never returned through normal API responses

The initial authorization model contains:

```text
user
admin
```

Regular users operate on resources permitted by the application authorization
model.

Administrative users receive broader management capabilities.

Authorization enforcement occurs in FastAPI.

The frontend may hide or display functionality according to role, but those
checks are not treated as security enforcement.

---

## 12. Kubernetes Runtime Design

Amazon EKS provides the production-style Kubernetes runtime.

Application workloads are separated into Kubernetes resources for:

- frontend
- backend
- worker

Supporting platform workloads include:

- Argo CD
- AWS Load Balancer Controller
- Secrets Store CSI components
- EKS-managed supporting services

Application workloads run in the:

```text
platform-launchpad
```

namespace.

Argo CD runs in:

```text
argocd
```

and the AWS Load Balancer Controller runs in:

```text
kube-system
```

Kubernetes health probes are used so workload availability is based on
application health rather than merely process existence.

---

## 13. GitOps Design

Runtime application configuration is maintained separately from application
source code.

The GitOps repository contains:

- base Kubernetes resources
- environment overlays
- ingress configuration
- application image references
- Argo CD Application resources
- platform Helm values

The development application is represented by the Argo CD Application:

```text
platform-launchpad-development
```

The AWS Load Balancer Controller is represented independently by:

```text
aws-load-balancer-controller-development
```

This allows platform services and application workloads to have separate
reconciliation boundaries.

### Reconciliation Flow

```text
Git commit
    |
    v
GitOps repository
    |
    v
Argo CD
    |
    v
Kubernetes desired-state comparison
    |
    +---- no difference ---> Synced
    |
    +---- difference ------> reconcile
```

Rollback is performed by restoring a known-good Git state or immutable image
reference rather than manually modifying the running cluster.

---

## 14. Database Migration Design

Database schema changes are part of application delivery.

Alembic migrations execute through a Kubernetes Job configured as an Argo CD
Sync hook.

Conceptually:

```text
GitOps change
     |
     v
Argo CD sync
     |
     v
database-migration Job
     |
     v
Alembic upgrade
     |
     v
application reconciliation
```

Argo CD records the migration hook result as part of the synchronization
operation.

This provides a visible deployment relationship between application
configuration and database schema evolution.

Migration failure can therefore prevent a deployment from being considered a
successful synchronization.

---

## 15. Ingress and TLS Design

External application traffic enters through an AWS Application Load Balancer.

The Kubernetes Ingress resource is reconciled by the AWS Load Balancer
Controller.

The application hostname is:

```text
launchpad.christineadelusi.com
```

TLS is terminated using an AWS Certificate Manager certificate.

The listener model is:

```text
HTTP :80
   |
   +---- redirect ----> HTTPS :443
                         |
                         v
                        ALB
                         |
                         v
                 Kubernetes services
```

Ingress routing exposes frontend traffic and selected backend API paths while
preserving Kubernetes service boundaries.

---

## 16. AWS Load Balancer Controller Design

The AWS Load Balancer Controller is treated as a platform dependency rather
than an application workload.

Its deployment is managed by Argo CD through a Helm-based Application.

Environment-specific Helm values are stored in the GitOps repository.

The controller uses a private Amazon ECR image.

This establishes the following ownership model:

```text
Terraform
   |
   +---- AWS prerequisites
   |
   +---- IAM / ECR / networking

Argo CD
   |
   +---- AWS Load Balancer Controller runtime
```

Terraform therefore provisions the infrastructure required by the controller,
while GitOps manages the Kubernetes runtime installation.

---

## 17. Secrets Management Design

Runtime secrets are not committed to Git.

AWS Secrets Manager stores sensitive application configuration.

Kubernetes workloads consume secrets through the Secrets Store CSI Driver and
a `SecretProviderClass`.

This creates a boundary between:

```text
Git
 |
 +---- non-secret desired state

AWS Secrets Manager
 |
 +---- sensitive runtime values
```

Workloads obtain only the AWS permissions required for their runtime
responsibilities.

This reduces reliance on long-lived static AWS credentials inside containers.

---

## 18. Container Supply Chain

Amazon ECR is the private container registry for the platform.

Repositories include application and platform runtime images.

The platform also mirrors selected upstream platform images into private ECR,
including the images required by the Argo CD bootstrap.

Pinned Argo CD bootstrap dependencies include:

- Argo CD
- Dex
- Redis

Mirroring these dependencies provides:

- controlled runtime image sources
- reproducible versions
- reduced dependence on public registries during cluster bootstrap
- clearer artifact ownership

The bootstrap process validates that the generated Argo CD installation
manifest no longer contains public runtime image references before applying
it.

---

## 19. Terraform Design

Terraform manages AWS infrastructure through reusable modules.

Current infrastructure modules cover concerns including:

- networking
- security groups
- Amazon EKS
- Amazon RDS
- Amazon ECR
- Argo CD ECR repositories
- controller ECR
- IAM
- CI delivery IAM
- application runtime IAM
- workload AWS access
- AWS Load Balancer Controller IAM
- Secrets Manager
- VPC endpoints
- Redis-related infrastructure

Environment configuration is separated under:

```text
terraform/environments/
```

The development environment consumes these modules and maintains independent
Terraform state.

Remote state uses AWS services appropriate for shared and recoverable
infrastructure management.

Terraform plans are used as drift-detection evidence.

A clean plan should report:

```text
No changes. Your infrastructure matches the configuration.
```

before a validated environment is considered infrastructure-stable.

---

## 20. Networking Design

The AWS environment uses a VPC divided across multiple Availability Zones.

The design separates:

- public ingress
- private application workloads
- private database access
- controlled outbound connectivity

The Application Load Balancer is internet-facing.

Application compute remains within private networking boundaries.

Private application subnets have controlled NAT egress where external access
is operationally required.

VPC endpoints are used for selected AWS services to reduce unnecessary public
network traversal.

---

## 21. Continuous Integration Design

Jenkins represents the continuous integration and artifact-delivery boundary.

Its responsibilities are intentionally separated from runtime deployment.

The target CI workflow is:

```text
Developer
    |
    v
Git repository
    |
    v
Jenkins
    |
    +---- tests
    +---- quality checks
    +---- security checks
    +---- container build
    +---- image scan
    +---- ECR publish
    |
    v
GitOps repository update
    |
    v
Argo CD
```

This prevents the CI system from becoming a second Kubernetes deployment
controller.

The GitOps repository remains the runtime deployment source of truth.

---

## 22. Argo CD Bootstrap Design

Argo CD creates a bootstrap dependency problem:

Argo CD is needed to manage GitOps applications, but Argo CD itself must exist
before it can reconcile those applications.

Platform Launchpad handles this through a dedicated bootstrap process.

Bootstrap automation:

1. reads environment information from Terraform outputs
2. validates required tooling
3. validates AWS identity
4. updates Kubernetes access
5. authenticates to private ECR
6. verifies or mirrors pinned Argo CD runtime images
7. downloads the pinned upstream Argo CD manifest
8. rewrites public image references to private ECR
9. validates that public runtime references are absent
10. installs Argo CD
11. waits for workloads to become ready
12. validates required CRDs
13. validates runtime images
14. applies GitOps Application resources

Bootstrap configuration is maintained under:

```text
bootstrap/argocd/
```

The process is designed to be idempotent so it can safely be rerun during
rebuild validation.

---

## 23. Observability Design

The application exposes operational signals through:

- structured application logs
- Kubernetes pod status
- liveness probes
- readiness probes
- deployment-worker logs
- API request logs

The broader observability architecture is designed to support:

- Prometheus-compatible metrics
- Grafana visualization
- CloudWatch
- OpenTelemetry
- distributed tracing
- application and platform alerting

Important signals include:

- API request rate
- API errors
- request latency
- authentication failures
- deployment requests by state
- worker processing duration
- worker failures
- database connectivity
- pod availability
- Kubernetes resource utilization

Observability capabilities can be expanded independently from the core
application delivery architecture.

---

## 24. Failure Handling

Failure handling is explicit rather than implicit.

The design uses:

- database transactions
- durable deployment-request state
- explicit failed lifecycle states
- worker retry behavior
- structured logs
- readiness probes
- liveness probes
- Kubernetes reconciliation
- Argo CD synchronization state
- Terraform drift detection

A deployment request should not disappear simply because a worker process
restarts.

Likewise, Kubernetes configuration should not depend on undocumented manual
cluster changes.

---

## 25. Scalability

Frontend and backend services are stateless and may be horizontally scaled.

Worker replicas may also be increased when the work-claiming model safely
supports additional concurrency.

Persistent application state remains in PostgreSQL.

Kubernetes provides the runtime foundation for replica scaling and future
Horizontal Pod Autoscaler policies.

Scaling policies should be introduced from measured workload requirements
rather than arbitrary replica counts.

---

## 26. Platform Rebuild Strategy

The AWS environment is intentionally reconstructable.

The rebuild model is:

```text
Terraform
    |
    v
AWS infrastructure
    |
    v
EKS cluster
    |
    v
Argo CD bootstrap
    |
    v
GitOps Applications
    |
    v
Application + platform workloads
```

This separation is important because Terraform cannot rely on Argo CD before
the cluster and its AWS prerequisites exist.

Likewise, application GitOps reconciliation cannot occur until Argo CD itself
has been bootstrapped.

The repository therefore explicitly documents and automates this dependency
order.

---

## 27. Cost-Control Strategy

The development AWS environment is not intended to run continuously merely to
keep the portfolio repository useful.

After validation and evidence collection, costly runtime resources can be
destroyed.

Source-controlled assets remain available:

- Terraform configuration
- application source
- GitOps manifests
- bootstrap scripts
- architecture documentation
- ADRs
- CI/CD definitions

The environment can later be reconstructed for demonstrations, additional
testing, or interview preparation.

This approach demonstrates both technical reproducibility and operational cost
awareness.

---

## 28. Design Evolution

The implemented platform differs from the original Sprint 0 design in several
important ways.

### Worker Queue

**Original design:** Redis-backed background queue.

**Implemented design:** database-backed deployment-request processing for the
currently validated workflow.

**Reason:** reduced unnecessary operational complexity while retaining durable
asynchronous processing.

### Kubernetes

**Original design:** Kubernetes was a later milestone.

**Implemented design:** Amazon EKS now hosts the deployed application and
platform services.

### Terraform

**Original design:** infrastructure automation was deferred.

**Implemented design:** AWS infrastructure is modularized and managed through
Terraform with drift validation.

### GitOps

**Original design:** Argo CD was a future delivery component.

**Implemented design:** Argo CD is the runtime reconciliation authority for
application workloads and the AWS Load Balancer Controller.

### Database Migrations

**Original design:** Alembic was part of application schema management but the
runtime migration mechanism was not finalized.

**Implemented design:** migrations execute through an Argo CD Sync-hook Job.

### Secrets

**Original design:** secrets would not be committed to Git.

**Implemented design:** AWS Secrets Manager and the Secrets Store CSI Driver
provide the runtime secret path.

### TLS and Ingress

**Original design:** AWS Application Load Balancer and ACM were planned.

**Implemented design:** the public application uses ALB ingress, ACM TLS, and
HTTP-to-HTTPS redirection.

### Platform Bootstrap

**Original design:** cluster bootstrap behavior was not fully defined.

**Implemented design:** Argo CD bootstrap is automated with pinned versions,
private ECR mirrors, manifest rewriting, validation, and idempotent GitOps
application installation.

---

## 29. Current Validation State

The development environment has been validated with:

- Terraform reporting no infrastructure drift
- Argo CD application reconciliation reporting `Synced`
- Argo CD application health reporting `Healthy`
- frontend pod running
- backend pod running
- worker pod running
- AWS Load Balancer Controller running
- HTTPS application access returning successfully
- backend readiness confirming database connectivity
- deployment worker successfully processing requests
- Argo CD database migration hook succeeding
- Argo CD bootstrap automation validated
- GitOps Application bootstrap validated

This validation demonstrates that the architecture is not only documented but
has been exercised as a running system.

---

## 30. Related Architecture Decisions

Detailed architectural rationale is maintained in the ADR collection under:

```text
docs/adr/
```

Important decisions include:

- use Platform Launchpad as the portfolio application
- use Next.js and FastAPI
- use PostgreSQL as the system of record
- use JWT authentication
- use GitOps for runtime deployment
- separate CI from runtime deployment
- preserve environment history through logical destruction
- enforce authorization in FastAPI
- use immutable container image digests
- use separate Terraform state per environment
- use OpenTelemetry for distributed tracing

ADRs remain the authoritative record for individual architectural decisions,
while this document explains how those decisions fit together as a technical
system.

---

## 31. Summary

Platform Launchpad evolved from an application-focused MVP into a
production-style platform engineering implementation.

The resulting architecture separates:

```text
Application development
        |
Continuous integration
        |
Artifact publication
        |
GitOps desired state
        |
Runtime reconciliation
        |
AWS / Kubernetes infrastructure
```

Terraform owns infrastructure.

Jenkins owns continuous integration and artifact delivery.

Git owns desired runtime configuration.

Argo CD owns Kubernetes reconciliation.

FastAPI owns application authorization and lifecycle APIs.

PostgreSQL owns durable application state.

The deployment worker owns asynchronous lifecycle processing.

AWS services provide the infrastructure, identity, networking, secret,
database, registry, and ingress foundations required to operate the platform.

Together, these boundaries make the platform reproducible, auditable,
recoverable, secure, and suitable for demonstrating senior-level DevOps and
platform engineering practices.