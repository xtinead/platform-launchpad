# Platform Launchpad

Platform Launchpad is a production-style AWS platform demonstrating how
infrastructure provisioning, continuous integration, GitOps delivery, secrets
management, database migrations, Kubernetes ingress, validation, and
infrastructure lifecycle management can operate as one cohesive engineering
system.

Terraform provisions the AWS foundation, Jenkins builds and publishes
immutable application artifacts, and Argo CD owns runtime reconciliation on
Amazon EKS. Workloads run in private subnets using AWS-native identity and
secret delivery, while documented validation, teardown, recovery, and rebuild
workflows demonstrate the complete platform lifecycle.

## Platform at a Glance

| Capability | Implementation |
| --- | --- |
| Infrastructure | Terraform + AWS |
| Runtime | Amazon EKS |
| Continuous Integration | Jenkins |
| Continuous Delivery | Argo CD + GitOps |
| Container Registry | Amazon ECR |
| Runtime Identity | EKS Pod Identity + IAM |
| Secrets | AWS Secrets Manager + Secrets Store CSI Driver |
| Data | Amazon RDS PostgreSQL + ElastiCache Redis |
| Ingress | Application Load Balancer + Route 53 + ACM |
| Application | Next.js + FastAPI + Python worker |
| Lifecycle | Provision → Validate → Destroy → Recover → Rebuild |

## What This Project Demonstrates

Platform Launchpad focuses on the engineering boundaries required to operate a
cloud-native application platform rather than only demonstrating application
deployment.

Key capabilities include:

- reproducible AWS infrastructure managed through Terraform;
- private Amazon EKS application workloads distributed across Availability
  Zones;
- separation of continuous integration from Kubernetes deployment authority;
- immutable container delivery through private Amazon ECR repositories;
- pull-based runtime reconciliation through Argo CD;
- AWS-native workload identity through EKS Pod Identity;
- runtime secret delivery from AWS Secrets Manager through the Secrets Store
  CSI Driver;
- automated Alembic database migrations integrated with Argo CD synchronization;
- HTTPS ingress through the AWS Load Balancer Controller, ACM, and Route 53;
- Terraform drift validation and idempotent platform bootstrap;
- controlled infrastructure teardown, residual-resource recovery, and
  post-destroy verification.

## Validated Platform Status

The development environment was deployed and validated end to end on AWS before
being intentionally destroyed to control ongoing cloud cost.

Validation confirmed:

- Amazon EKS worker nodes and application workloads were healthy;
- the frontend, backend, and asynchronous worker operated successfully;
- PostgreSQL and Redis-backed application workflows functioned correctly;
- Argo CD Applications reached `Synced` and `Healthy`;
- database migrations executed automatically through an Argo CD Sync hook;
- runtime secrets were delivered from AWS Secrets Manager;
- public application traffic was served through HTTPS using an AWS Application
  Load Balancer and ACM certificate;
- Terraform reported zero infrastructure drift;
- Argo CD and GitOps bootstrap workflows were successfully rerun to validate
  idempotency;
- the complete development environment was subsequently torn down and verified.

The validated endpoint was:

```text
https://launchpad.christineadelusi.com
```

The endpoint is not expected to remain online continuously. The development
platform is intentionally ephemeral and can be recreated through Terraform and
the documented bootstrap process.

---

## Architecture

Platform Launchpad separates infrastructure provisioning, artifact production,
and runtime reconciliation into distinct control planes.

```text
                         Application Repository
                                  |
                                  v
                               Jenkins
                         test / build / publish
                                  |
                                  v
                           Amazon ECR
                        immutable images
                                  |
                                  v
                           GitOps Repository
                                  |
                                  v
                               Argo CD
                         desired-state reconciliation
                                  |
                                  v
+------------------------------------------------------------------+
|                              AWS                                 |
|                                                                  |
|  Route 53 -> ACM -> Application Load Balancer                    |
|                         |                                        |
|                         v                                        |
|  +------------------------------------------------------------+  |
|  |                Private Application Subnets                 |  |
|  |                                                            |  |
|  |                     Amazon EKS                             |  |
|  |                                                            |  |
|  |       Frontend        Backend         Worker               |  |
|  |                          |               |                 |  |
|  +--------------------------|---------------|-----------------+  |
|                             |               |                    |
|                             v               v                    |
|                     RDS PostgreSQL   ElastiCache Redis           |
|                                                                  |
|  Secrets Manager -> Secrets Store CSI -> Application Workloads   |
|                                                                  |
+------------------------------------------------------------------+
```

Terraform provisions the AWS foundation independently of runtime application
delivery. Jenkins owns continuous integration and artifact publication, while
Argo CD owns Kubernetes deployment and reconciliation.

This separation prevents the CI system from becoming the Kubernetes deployment
control plane and keeps Git as the source of truth for runtime desired state.

Detailed architecture:

- [System Architecture](docs/architecture/system-architecture.md)
- [Technical Design](docs/architecture/technical-design.md)

## Delivery Model

The delivery workflow deliberately separates **CI** from **CD**.

```text
Application change
       |
       v
Application repository
       |
       v
Jenkins
  |-- test
  |-- build
  |-- publish
       |
       v
Private Amazon ECR
       |
       | immutable image digest
       v
GitOps desired-state change
       |
       v
GitOps repository
       |
       v
Argo CD
       |
       | pull / reconcile
       v
Amazon EKS
```

### Continuous Integration

Jenkins is responsible for producing deployable artifacts. Its responsibilities
include application validation, container image creation, and publication to
private Amazon ECR repositories.

Application images are referenced by immutable ECR digests rather than mutable
deployment tags.

### Continuous Delivery

Argo CD is responsible for runtime Kubernetes delivery.

The GitOps repository defines the desired state for:

- backend Deployment and Service;
- frontend Deployment and Service;
- worker Deployment;
- runtime ServiceAccounts;
- SecretProviderClass;
- database migration Job;
- application Ingress;
- AWS Load Balancer Controller.

Jenkins does **not** deploy application workloads directly with `kubectl`.
Runtime changes become GitOps desired-state changes, and Argo CD reconciles
those changes into Amazon EKS.

This provides a clear ownership boundary:

```text
Jenkins -> Build and publish artifacts
Git     -> Store runtime desired state
Argo CD -> Reconcile desired state
EKS     -> Run application workloads
```

## Application Runtime

Platform Launchpad contains three primary application workloads:

- **Frontend** — Next.js web interface;
- **Backend** — FastAPI REST API;
- **Worker** — asynchronous deployment-request processor.

The backend provides health, authentication, environment, and
deployment-request APIs. Deployment requests are accepted asynchronously and
processed by the worker, with validated requests successfully transitioning to
`succeeded`.

---

## Platform Infrastructure

Terraform provisions the AWS foundation that supports the application and
delivery platform.

Key infrastructure includes:

- VPC networking across public, private application, and private database
  subnets;
- Amazon EKS and managed worker nodes;
- Amazon RDS PostgreSQL;
- Amazon ElastiCache Redis;
- private Amazon ECR repositories;
- IAM roles, policies, and EKS Pod Identity associations;
- AWS Secrets Manager;
- Application Load Balancer integration;
- NAT-based outbound access for private workloads;
- VPC endpoints and security groups supporting private service communication.

Terraform state is isolated by environment to reduce blast radius and support
independent lifecycle management.

The development environment is intentionally ephemeral. Infrastructure can be
provisioned for validation and destroyed afterward to control cloud cost while
preserving a reproducible rebuild path.

Detailed infrastructure design:

- [Terraform Design](docs/infrastructure/terraform-design.md)
- [Teardown and Rebuild](docs/infrastructure/teardown-rebuild.md)

## Security and Identity

Platform Launchpad applies AWS-native and Kubernetes-native security boundaries
throughout the runtime architecture.

Security controls include:

- application workloads run in private subnets;
- RDS PostgreSQL and ElastiCache Redis are not publicly exposed;
- Kubernetes workloads use dedicated ServiceAccounts;
- AWS permissions are delivered through IAM roles and EKS Pod Identity;
- application credentials remain in AWS Secrets Manager;
- Secrets Store CSI Driver mounts runtime secret values into workloads;
- application containers run as non-root;
- privilege escalation is disabled;
- Linux capabilities are dropped where applicable;
- root filesystems are read-only where supported;
- public application traffic is encrypted using ACM-managed TLS;
- the EKS public API endpoint is CIDR restricted;
- application releases use immutable ECR image digests.

Runtime secret delivery follows this model:

```text
Kubernetes ServiceAccount
          |
          v
    EKS Pod Identity
          |
          v
       IAM Role
          |
          v
 AWS Secrets Manager
          |
          v
Secrets Store CSI Driver
          |
          v
 Backend / Worker / Migration Job
```

The application consumes sensitive runtime values such as `database_url` and
`secret_key` through this mechanism rather than committing them to Git or
embedding them directly in Kubernetes manifests.

Detailed security design:

- [Security Model](docs/security/security-model.md)

## Database Migration Strategy

Schema migrations are integrated into GitOps synchronization rather than run as
a separate manual operational step.

An Argo CD Sync hook executes:

```text
alembic upgrade head
```

before the application workloads proceed through normal reconciliation.

The synchronization order is designed so that foundational resources exist
before migrations execute and application workloads are reconciled only after
the migration stage succeeds.

Conceptually:

```text
Namespace
    |
    v
ServiceAccounts + SecretProviderClass
    |
    v
Database Migration Job
    |
    v
Backend + Worker + Frontend + Services
    |
    v
Ingress
```

A failed migration prevents the deployment from being treated as successfully
synchronized, reducing the risk of releasing application code against an
incompatible database schema.

Detailed database design:

- [Database Design](docs/database/database-design.md)

## Platform Bootstrap

Argo CD is installed through a deterministic bootstrap process under:

```text
bootstrap/argocd/
```

The bootstrap workflow:

- validates required tooling and AWS account context;
- updates Kubernetes access for the target EKS cluster;
- authenticates to private Amazon ECR repositories;
- mirrors or reuses pinned Argo CD runtime images;
- rewrites public image references to private ECR;
- applies the Argo CD installation;
- waits for platform workloads and required CRDs;
- verifies that public runtime image references are not retained;
- registers the initial GitOps Applications.

The bootstrap process has been validated as safe to rerun against an existing
platform, supporting idempotent recovery and rebuild workflows.

Detailed bootstrap documentation:

- [Argo CD Bootstrap](bootstrap/argocd/README.md)

---

## Infrastructure Lifecycle

Platform Launchpad was designed to support the complete infrastructure
lifecycle rather than only initial provisioning.

The validated development lifecycle is:

```text
Terraform Provision
        |
        v
Argo CD Bootstrap
        |
        v
GitOps Reconciliation
        |
        v
Application Validation
        |
        v
Evidence Capture
        |
        v
Controlled Teardown
        |
        v
Residual Recovery
        |
        v
Post-Destroy Verification
        |
        v
Deterministic Rebuild
```

During the real development teardown, several lifecycle edge cases were
identified, including non-empty ECR repositories, retained Jenkins IAM
credentials, an orphaned EKS network interface, and an EKS-generated security
group.

The recovery process preserved Terraform ownership wherever possible, applied
narrow cleanup only to confirmed residual resources, regenerated destroy plans
after partial teardown, and converted the lessons learned into reusable
automation.

Teardown tooling is maintained under:

```text
bootstrap/teardown/
├── prepare-destroy.sh
├── cleanup-eks-residuals.sh
└── verify-destroy.sh
```

Development-specific Terraform configuration explicitly permits destructive
cleanup for disposable resources while shared module defaults remain
conservative.

Detailed lifecycle documentation:

- [Teardown and Rebuild](docs/infrastructure/teardown-rebuild.md)
- [Engineering Case Study](docs/case-study.md)

## Validation Evidence

The development platform was validated end to end before teardown.

### Application

![Platform Launchpad dashboard](docs/screenshots/application/01-dashboard.png)

The application dashboard demonstrated authenticated access, environment
visibility, deployment tracking, role-aware navigation, and live backend
connectivity.

### GitOps

![Argo CD applications](docs/screenshots/argocd/01-applications-overview.png)

The primary Argo CD Applications were validated as:

```text
aws-load-balancer-controller-development   Synced   Healthy
platform-launchpad-development             Synced   Healthy
```

### Kubernetes Runtime

![Platform Launchpad workloads](docs/screenshots/kubernetes/01-application-workloads.png)

The frontend, backend, and worker workloads were validated as running
successfully on Amazon EKS.

### Terraform Drift Validation

![Terraform zero-drift validation](docs/screenshots/infrastructure/01-terraform-zero-drift.png)

The final infrastructure validation reported:

```text
No changes. Your infrastructure matches the configuration.
```

Additional evidence is available under:

```text
docs/screenshots/
├── application/
├── argocd/
├── infrastructure/
└── kubernetes/
```

## Key Engineering Decisions

Important architectural decisions are documented as ADRs under `docs/adr/`.

Key decisions include:

- use GitOps for runtime Kubernetes delivery;
- separate CI from deployment authority;
- use immutable container image digests;
- isolate Terraform state by environment;
- use AWS-native workload identity;
- preserve environment history through logical destruction;
- integrate database migrations with GitOps synchronization;
- use OpenTelemetry for distributed tracing.

These decisions are documented individually so that tradeoffs, context, and
consequences remain visible rather than being embedded only in implementation
code.

## Repository Structure

```text
platform-launchpad/
├── backend/
├── frontend/
├── worker/
├── bootstrap/
│   ├── argocd/
│   └── teardown/
├── terraform/
│   ├── bootstrap/
│   ├── environments/
│   ├── modules/
│   └── policies/
├── jenkins/
├── docker/
├── deploy/
└── docs/
    ├── adr/
    ├── api/
    ├── architecture/
    ├── cicd/
    ├── database/
    ├── infrastructure/
    ├── observability/
    ├── product/
    ├── project-management/
    ├── screenshots/
    ├── security/
    └── wireframes/
```

Runtime Kubernetes desired state is maintained separately in the
`platform-launchpad-gitops` repository.

This separation reinforces the boundary between CI-produced artifacts and
GitOps-managed runtime state.

## Documentation Map

| Area | Documentation |
| --- | --- |
| Architecture | [System Architecture](docs/architecture/system-architecture.md) |
| Technical Design | [Technical Design](docs/architecture/technical-design.md) |
| Infrastructure | [Terraform Design](docs/infrastructure/terraform-design.md) |
| Lifecycle | [Teardown and Rebuild](docs/infrastructure/teardown-rebuild.md) |
| CI/CD | [CI/CD Design](docs/cicd/cicd-design.md) |
| Security | [Security Model](docs/security/security-model.md) |
| Observability | [Observability Design](docs/observability/observability-design.md) |
| Database | [Database Design](docs/database/database-design.md) |
| API | [API Specification](docs/api/api-specification.md) |
| Architecture Decisions | [Architecture Decision Records](docs/adr/) |
| Engineering Case Study | [Case Study](docs/case-study.md) |

## Technology Stack

| Category | Technologies |
| --- | --- |
| Cloud | AWS |
| Infrastructure as Code | Terraform |
| Containers | Docker, Amazon ECR |
| Kubernetes | Amazon EKS |
| CI | Jenkins |
| CD / GitOps | Argo CD |
| Backend | FastAPI, Python |
| Frontend | Next.js |
| Database | PostgreSQL |
| Cache | Redis |
| Migrations | Alembic |
| Identity | IAM, EKS Pod Identity |
| Secrets | AWS Secrets Manager, Secrets Store CSI Driver |
| Networking | VPC, ALB, Route 53, ACM |
| Observability | OpenTelemetry |

## Project Status

The development environment has been successfully:

```text
Provisioned
Validated
Documented
Evidence-captured
Destroyed
Verified
```

The AWS environment is intentionally not kept running continuously in order to
control cloud cost.

The platform can be recreated using Terraform, the Argo CD bootstrap process,
and the GitOps repository.

The project now serves as a reproducible platform engineering reference
implementation and interview portfolio demonstrating infrastructure,
delivery, security, GitOps, lifecycle management, and operational recovery.
