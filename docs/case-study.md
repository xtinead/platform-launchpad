# Platform Launchpad — Platform Engineering Case Study

## 1. Executive Summary

Platform Launchpad is a production-style platform engineering portfolio project
designed to demonstrate how an application can be built, secured, delivered,
operated, and recovered on AWS using modern DevOps and GitOps practices.

The project combines:

- application development;
- infrastructure as code;
- Kubernetes;
- private container delivery;
- secrets management;
- workload identity;
- GitOps;
- database migrations;
- public ingress;
- HTTPS;
- operational validation;
- teardown and rebuild capability.

The platform is implemented with:

```text
AWS
Terraform
Amazon EKS
Kubernetes
Amazon ECR
Amazon RDS
ElastiCache Redis
AWS Secrets Manager
EKS Pod Identity
Secrets Store CSI Driver
Jenkins
Argo CD
GitOps
AWS Load Balancer Controller
Application Load Balancer
AWS Certificate Manager
Route 53
FastAPI
Next.js
Python
Alembic
PostgreSQL
```

The project was built as a realistic Senior DevOps / Platform Engineer
portfolio artifact rather than as a simple application deployment.

---

## 2. Problem Statement

A traditional application deployment often places too much operational
responsibility in a single pipeline.

Common risks include:

- CI systems holding cluster-admin credentials;
- direct `kubectl` deployment from Jenkins;
- mutable image tags;
- manually managed infrastructure;
- secrets stored in manifests;
- inconsistent database migrations;
- poor recovery procedures;
- undocumented cloud dependencies;
- infrastructure left running unnecessarily.

Platform Launchpad was designed to address those issues by separating the
platform into clear ownership boundaries.

---

## 3. Engineering Goals

The main goals were:

- provision AWS infrastructure declaratively;
- deploy application workloads to Kubernetes;
- separate CI from runtime deployment;
- use Git as the Kubernetes desired-state source of truth;
- use immutable container artifacts;
- keep runtime secrets outside Git;
- provide workload-specific AWS identity;
- automate database schema migration;
- expose the application securely over HTTPS;
- make the platform rebuildable;
- validate the complete application workflow;
- control AWS cost through deliberate teardown.

---

## 4. Architecture

The final platform follows this ownership model:

```text
Application Repository
        |
        v
Jenkins CI
        |
        +---- test
        +---- scan
        +---- build
        |
        v
Private Amazon ECR
        |
        v
Immutable Image Digest
        |
        v
GitOps Repository
        |
        v
Argo CD
        |
        +---- Database Migration Hook
        |
        v
Amazon EKS
```

AWS infrastructure is provisioned separately through:

```text
Terraform
    |
    v
VPC
EKS
IAM
ECR
RDS
Redis
Secrets Manager
VPC Endpoints
NAT
Security Groups
```

---

## 5. Application Architecture

Platform Launchpad contains three primary runtime workloads.

### Frontend

Technology:

```text
Next.js
React
TypeScript
```

Responsibilities include:

- authentication UI;
- environment management;
- deployment-request submission;
- deployment status presentation.

---

### Backend

Technology:

```text
FastAPI
SQLAlchemy
Alembic
PostgreSQL
JWT
```

Responsibilities include:

- authentication;
- authorization;
- environment CRUD;
- deployment requests;
- audit data;
- health endpoints;
- readiness checks.

---

### Worker

Technology:

```text
Python
```

The worker processes persisted deployment requests asynchronously.

The implemented model uses:

```text
database-backed polling
```

rather than requiring Redis as the primary deployment-request queue.

Validated worker behavior includes successful transitions to:

```text
succeeded
```

---

## 6. Infrastructure Architecture

Terraform provisions the AWS foundation.

Implemented modules include:

```text
application-runtime-iam
argocd-ecr
ci-delivery-iam
controller-ecr
ecr
eks
eks-workload-access
iam
load-balancer-controller-iam
networking
rds
redis
secrets
security-groups
vpc-endpoints
```

The infrastructure includes:

- multi-AZ VPC;
- public subnets;
- private application subnets;
- private database subnets;
- NAT Gateway;
- EKS;
- managed node group;
- private ECR repositories;
- RDS PostgreSQL;
- ElastiCache Redis;
- Secrets Manager;
- Pod Identity;
- VPC endpoints;
- security groups;
- remote Terraform state.

---

## 7. GitOps Architecture

Runtime Kubernetes state is stored in:

```text
platform-launchpad-gitops
```

Argo CD Applications:

```text
platform-launchpad-development
aws-load-balancer-controller-development
```

Both were validated as:

```text
Synced
Healthy
```

Argo CD owns runtime reconciliation.

Jenkins does not directly deploy normal application workloads with
`kubectl`.

---

## 8. CI/CD Separation

The platform intentionally separates:

```text
Continuous Integration
```

from:

```text
Continuous Delivery
```

Jenkins responsibilities:

- test;
- lint;
- scan;
- build;
- publish;
- update GitOps.

Argo CD responsibilities:

- detect desired-state changes;
- reconcile Kubernetes;
- manage deployment health;
- execute Sync hooks.

This reduces CI blast radius and produces a clearer audit trail.

---

## 9. Immutable Artifact Delivery

Application images are stored in private Amazon ECR.

GitOps manifests reference image digests.

Example:

```text
<repository>@sha256:<digest>
```

Benefits include:

- deterministic deployment;
- reproducible rollback;
- protection from mutable-tag drift;
- source-to-runtime traceability.

---

## 10. Database Migration Design

Alembic migrations run as an Argo CD Sync hook.

The migration Job executes:

```text
alembic upgrade head
```

before normal application synchronization completes.

Sync ordering:

```text
Wave -3
    Namespace

Wave -2
    ServiceAccounts
    SecretProviderClass

Wave -1
    Database Migration

Wave 0
    Application Workloads
```

Argo CD records migration success or failure as part of the deployment
operation.

---

## 11. Secrets Management

Runtime secrets are stored in:

```text
AWS Secrets Manager
```

Kubernetes retrieves them through:

```text
Secrets Store CSI Driver
```

Workloads use:

```text
EKS Pod Identity
```

for AWS access.

The application receives secret values through mounted files rather than
plaintext GitOps manifests.

Current secret values include:

```text
database_url
secret_key
```

---

## 12. Container Security

Application workloads use hardened Kubernetes security contexts.

Controls include:

```text
runAsNonRoot
allowPrivilegeEscalation=false
readOnlyRootFilesystem=true
drop Linux capabilities
```

where supported.

Application containers do not contain static AWS credentials.

---

## 13. Networking

The platform uses:

```text
Public Subnets
    |
    v
Private Application Subnets
    |
    v
Private Database Subnets
```

Public access terminates at the Application Load Balancer.

EKS workloads run privately.

RDS and Redis remain private.

Private application subnets use controlled NAT egress where external
connectivity is required.

VPC endpoints reduce public paths to selected AWS services.

---

## 14. HTTPS and DNS

Public hostname:

```text
launchpad.christineadelusi.com
```

The delivery path is:

```text
Route 53
    |
    v
AWS Application Load Balancer
    |
    v
ACM TLS
    |
    v
Kubernetes Ingress
```

Validated behavior:

```text
HTTP :80
    -> 301 redirect

HTTPS :443
    -> HTTP/2 200
```

---

## 15. Cross-Account DNS Boundary

The Route 53 hosted zone exists in a separate AWS development account from the
application runtime account.

This created a real cross-account operational boundary.

The DNS record was created in the hosted-zone account while the ALB existed in
the runtime account.

This distinction is documented rather than hidden.

---

## 16. Argo CD Bootstrap Challenge

One of the major platform problems was:

```text
Argo CD is needed to manage GitOps workloads,
but Argo CD must already exist before it can reconcile them.
```

The solution was a dedicated bootstrap layer.

---

## 17. Argo CD Bootstrap Solution

The main repository contains:

```text
bootstrap/argocd/
```

with:

```text
images.env
install.sh
rewrite_manifest.py
apply-applications.sh
README.md
```

The bootstrap:

1. reads Terraform outputs;
2. validates AWS identity;
3. updates kubeconfig;
4. authenticates to ECR;
5. checks required bootstrap images;
6. mirrors missing images;
7. downloads a pinned Argo CD manifest;
8. rewrites public runtime image references;
9. validates the rewritten manifest;
10. installs Argo CD;
11. validates CRDs and workloads;
12. applies initial GitOps Applications.

---

## 18. Private Argo CD Runtime Images

Pinned bootstrap dependencies:

```text
Argo CD  v3.5.2
Dex      v2.45.1
Redis    8.2.3-alpine
```

These are mirrored into private Terraform-managed ECR repositories.

This reduces runtime dependence on public registries and improves rebuild
consistency.

---

## 19. Terraform Adoption of Existing Resources

During implementation, some Argo CD ECR repositories existed before Terraform
owned them.

Rather than recreate them, the resources were adopted through:

```text
terraform import
```

The adoption process was:

```text
Declare Resource
    |
    v
Import Existing AWS Resource
    |
    v
Terraform Plan
    |
    v
Review Differences
    |
    v
Apply Safe Reconciliation
    |
    v
Zero Drift
```

This was an important infrastructure-management exercise.

---

## 20. Ingress Failure and Root Cause

During deployment, the application hostname initially returned:

```text
404 Not Found
```

from the ALB.

The Kubernetes Ingress appeared to contain the expected host, but the rendered
resource lost its HTTP path definitions.

Root cause:

```text
development Kustomize ingress patch
```

replaced the base rule structure and removed the HTTP paths.

---

## 21. Ingress Fix

The unnecessary development ingress patch was removed.

After rendering:

```text
/api
/docs
/redoc
/openapi.json
/health
/
```

were restored.

Argo CD reconciled the corrected Ingress and the ALB routing rules became
functional.

This demonstrated why rendered Kustomize output should be validated before
assuming source YAML produces the expected runtime object.

---

## 22. DNS Failure and Root Cause

The initial application URL failed with:

```text
Could not resolve host
```

Investigation showed that:

- the ALB existed;
- the Ingress existed;
- Route 53 had no record for the application hostname;
- the hosted zone existed in the separate development account.

A CNAME was created to the ALB hostname.

Public DNS resolvers then resolved the endpoint correctly.

A local DNS cache initially continued returning NXDOMAIN until the Windows DNS
resolver cache was flushed.

---

## 23. HTTPS Enablement

The application initially worked over HTTP.

HTTPS was added using:

- ACM certificate;
- HTTPS listener;
- ALB ingress annotations;
- HTTP-to-HTTPS redirect.

After reconciliation:

```text
HTTP -> 301
HTTPS -> HTTP/2 200
```

This completed the public ingress path.

---

## 24. Worker Startup Failure

The worker initially entered:

```text
CrashLoopBackOff
```

after the database infrastructure existed but before the database migrations
had been applied.

After running:

```text
alembic upgrade head
```

the required schema existed and the worker started successfully.

This exposed the need for automated migration ordering.

---

## 25. Database Migration Automation

The manual migration recovery step was replaced with a GitOps-controlled Sync
hook.

This changed the system from:

```text
Operator manually runs migration
```

to:

```text
Argo CD sync
    |
    v
Migration Job
    |
    v
Application reconciliation
```

The migration Job was later validated as:

```text
hookPhase: Succeeded
hookType: Sync
```

---

## 26. AWS Load Balancer Controller Ownership

The AWS Load Balancer Controller originally existed as a Helm-managed runtime
installation.

It was then moved under Argo CD ownership.

The ownership model became:

```text
Terraform
    |
    +---- IAM
    +---- ECR
    +---- networking prerequisites

Argo CD
    |
    +---- Helm release
```

The transition preserved the running controller and resulted in:

```text
Synced
Healthy
```

---

## 27. End-to-End Validation

The final environment was validated from infrastructure through application
workflow.

Terraform:

```text
No changes. Your infrastructure matches the configuration.
```

Argo CD:

```text
aws-load-balancer-controller-development
    Synced
    Healthy

platform-launchpad-development
    Synced
    Healthy
```

Kubernetes:

```text
backend     Running
frontend    Running
worker      Running
```

HTTPS:

```text
HTTP/2 200
```

Readiness:

```json
{
  "status": "ready",
  "checks": {
    "database": "ok"
  }
}
```

---

## 28. Functional Validation

The user workflow was tested through:

1. application access;
2. authentication;
3. environment creation;
4. deployment-request submission;
5. API acceptance;
6. worker processing;
7. successful completion.

Backend evidence included:

```text
POST .../deployment-requests HTTP/1.1" 202 Accepted
```

Worker evidence included:

```text
Processed deployment request <id> with status succeeded.
```

Multiple deployment requests were processed successfully.

---

## 29. Observability Validation

Current operational visibility includes:

- Kubernetes workload state;
- liveness probes;
- readiness probes;
- application logs;
- worker logs;
- Argo CD health;
- Argo CD sync;
- migration hook status;
- Terraform drift;
- public HTTPS validation.

A broader Prometheus/Grafana/OpenTelemetry observability stack remains planned
future work.

---

## 30. Key Engineering Decisions

Important decisions include:

### GitOps Runtime Delivery

Runtime Kubernetes state belongs in Git and Argo CD.

### CI/CD Separation

Jenkins does not directly deploy application workloads.

### Immutable Digests

Deployment artifacts use immutable image references.

### Externalized Secrets

Secrets remain in AWS Secrets Manager.

### Pod Identity

Workloads receive temporary AWS credentials through EKS Pod Identity.

### Private Data Services

RDS and Redis remain private.

### Controlled Migration

Schema migration is part of deployment orchestration.

### Reproducible Bootstrap

Argo CD installation is automated rather than dependent on undocumented
manual steps.

### Cost-Aware Lifecycle

The development environment can be destroyed after validation and recreated
when needed.

---

## 31. What Changed From the Original Design

The initial architecture evolved during implementation.

### Redis

Original:

```text
Redis task queue
```

Current:

```text
database-backed worker polling
```

Redis remains available for future capabilities.

### EKS

Original:

```text
future AWS runtime
```

Current:

```text
deployed and validated runtime
```

### Argo CD

Original:

```text
planned GitOps component
```

Current:

```text
runtime reconciliation authority
```

### Database Migrations

Original:

```text
Alembic available
```

Current:

```text
automated Argo CD Sync hook
```

### Argo CD Bootstrap

Original:

```text
not fully defined
```

Current:

```text
pinned, private-ECR, reproducible bootstrap
```

---

## 32. Recovery Model

The platform recovery sequence is:

```text
Terraform
    |
    v
AWS Infrastructure
    |
    v
Argo CD Bootstrap
    |
    v
GitOps Applications
    |
    v
Database Migration
    |
    v
Application Runtime
```

Representative commands:

```bash
terraform apply
```

then:

```bash
./bootstrap/argocd/install.sh
./bootstrap/argocd/apply-applications.sh
```

Argo CD then reconciles the runtime.

---

## 33. Cost Management

The development environment contains meaningful AWS cost drivers:

- EKS control plane;
- EC2 worker nodes;
- NAT Gateway;
- RDS;
- Redis;
- ALB;
- interface VPC endpoints.

The environment is not intended to remain online indefinitely.

The lifecycle is:

```text
Build
    |
    v
Validate
    |
    v
Capture Evidence
    |
    v
Destroy
    |
    v
Rebuild When Needed
```

This makes cost control part of platform operations.

---

## 34. Senior DevOps / Platform Engineering Skills Demonstrated

Platform Launchpad demonstrates:

- AWS architecture;
- Terraform;
- modular Infrastructure as Code;
- Terraform import;
- remote state;
- drift detection;
- EKS;
- Kubernetes;
- GitOps;
- Argo CD;
- Jenkins;
- private ECR;
- immutable artifacts;
- IAM;
- Pod Identity;
- Secrets Manager;
- Secrets Store CSI;
- RDS;
- Redis;
- VPC design;
- NAT;
- VPC endpoints;
- ALB;
- ACM;
- Route 53;
- CI/CD separation;
- database migration automation;
- operational troubleshooting;
- cross-account DNS;
- application health checks;
- platform recovery;
- cost-aware teardown.

---

## 35. Interview Discussion Points

Strong discussion topics include:

### Why GitOps?

Because runtime Kubernetes state should be auditable and pull-based rather than
owned by Jenkins credentials.

### Why image digests?

Because tags can move while digests identify the exact artifact.

### Why Pod Identity?

Because workloads need temporary AWS credentials without static access keys.

### Why database migration hooks?

Because application deployment and schema compatibility must be coordinated.

### Why private ECR mirrors for Argo CD?

Because bootstrap dependencies should be version-controlled and less dependent
on external registries.

### Why NAT and VPC endpoints together?

Because private workloads need external connectivity for some destinations,
while AWS service traffic can remain private where endpoints are supported.

### Why tear the environment down?

Because a portfolio environment should prove reproducibility rather than incur
continuous cost merely to remain idle.

---

## 36. Result

The final development environment successfully demonstrated:

```text
Terraform-managed AWS infrastructure
        |
        v
Reproducible Argo CD bootstrap
        |
        v
GitOps-managed Kubernetes platform
        |
        v
Automated database migration
        |
        v
Secure application runtime
        |
        v
HTTPS public access
        |
        v
Successful asynchronous deployment workflow
```

The project therefore demonstrates not only application deployment, but the
engineering of the platform that supports deployment, security, identity,
networking, recovery, operations, and cost control.

---

## 37. Validation Evidence

The following screenshots were captured from the validated AWS development
environment before teardown.

### Application

- [Dashboard](screenshots/application/01-dashboard.png)
- [Environment management](screenshots/application/02-environments.png)
- [Successful deployment request](screenshots/application/03-successful-deployment-request.png)

### Argo CD and GitOps

- [Applications overview](screenshots/argocd/01-applications-overview.png)
- [Platform Launchpad resource graph](screenshots/argocd/02-platform-launchpad-resource-graph.png)
- [AWS Load Balancer Controller reconciliation](screenshots/argocd/03-load-balancer-controller-synced.png)
- [Database migration Sync hook](screenshots/argocd/04-database-migration-hook.png)

### Kubernetes

- [Application workloads](screenshots/kubernetes/01-application-workloads.png)
- [Services and Ingress routing](screenshots/kubernetes/02-application-services-ingress.png)
- [Platform components](screenshots/kubernetes/03-platform-components.png)
- [Argo CD control plane](screenshots/kubernetes/04-argocd-control-plane.png)
- [EKS nodes](screenshots/kubernetes/05-eks-nodes.png)

### Infrastructure

- [Terraform zero drift](screenshots/infrastructure/01-terraform-zero-drift.png)
- [HTTPS validation](screenshots/infrastructure/02-https-validation.png)
- [Backend readiness](screenshots/infrastructure/03-backend-readiness.png)
- [Worker processing success](screenshots/infrastructure/04-worker-success.png)

Together, this evidence demonstrates the platform across four layers:

```text
Application
    |
    v
GitOps / Argo CD
    |
    v
Kubernetes / EKS
    |
    v
Terraform / AWS
```

---

## 38. Summary

Platform Launchpad evolved from a local application prototype into a
production-style AWS and Kubernetes platform.

The most important outcome is the separation of responsibilities:

```text
Terraform
    -> infrastructure

Jenkins
    -> CI and artifact delivery

ECR
    -> immutable artifacts

Git
    -> runtime desired state

Argo CD
    -> Kubernetes reconciliation

FastAPI
    -> application authorization and lifecycle APIs

PostgreSQL
    -> durable application state

Worker
    -> asynchronous lifecycle processing
```

This architecture provides a credible demonstration of Senior DevOps and
Platform Engineering practices while remaining reproducible enough to destroy
and rebuild as needed.