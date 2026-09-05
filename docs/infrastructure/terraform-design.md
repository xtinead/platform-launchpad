# Platform Launchpad — Terraform and AWS Infrastructure Design

## 1. Purpose

This document describes the as-built Terraform and AWS infrastructure
architecture for Platform Launchpad.

Terraform is the authoritative provisioning layer for the AWS runtime
foundation. It creates the network, compute, data, identity, registry,
secret-management, and platform prerequisites required before GitOps can
reconcile Kubernetes workloads.

The infrastructure is intentionally designed for:

- reproducibility;
- environment isolation;
- least-privilege access;
- private application networking;
- private data services;
- GitOps delivery;
- deterministic recovery;
- drift detection;
- controlled teardown;
- portfolio and interview demonstrations.

The authoritative application and Kubernetes topology is documented in:

```text
docs/architecture/system-architecture.md
```

---

## 2. Current Implementation Status

The AWS development environment has been provisioned and validated.

Implemented Terraform capabilities include:

- Amazon VPC;
- public subnets across multiple Availability Zones;
- private application subnets;
- private database subnets;
- Internet Gateway;
- public route table;
- private application route table;
- isolated database route table;
- NAT Gateway;
- NAT Elastic IP;
- application, ALB, database, Redis, and endpoint security groups;
- Amazon EKS;
- EKS managed node group;
- EKS access configuration;
- EKS Pod Identity Agent;
- EKS Pod Identity associations;
- Amazon RDS PostgreSQL;
- Amazon ElastiCache Redis;
- application Amazon ECR repository;
- AWS Load Balancer Controller ECR repository;
- Argo CD bootstrap ECR repositories;
- Amazon ECR lifecycle policies;
- AWS Secrets Manager runtime secret;
- application runtime IAM;
- worker IAM;
- CI delivery IAM;
- AWS Load Balancer Controller IAM;
- VPC endpoints;
- EKS-to-RDS network authorization;
- EKS-to-Redis network authorization;
- environment outputs required by bootstrap and runtime automation.

The current development environment has also passed:

```text
terraform plan
```

with:

```text
No changes. Your infrastructure matches the configuration.
```

---

## 3. Infrastructure Ownership Model

Platform Launchpad separates cloud infrastructure ownership from Kubernetes
runtime ownership.

```text
Terraform
    |
    | AWS infrastructure
    v
Amazon EKS
    |
    v
Bootstrap Automation
    |
    | installs Argo CD
    v
Argo CD
    |
    | Kubernetes desired state
    v
Application + Platform Workloads
```

### Terraform Owns

Terraform owns infrastructure such as:

- VPC;
- subnets;
- route tables;
- NAT;
- EKS;
- node groups;
- IAM;
- Pod Identity;
- RDS;
- Redis;
- ECR;
- Secrets Manager;
- VPC endpoints;
- security groups.

### Bootstrap Automation Owns

Bootstrap automation establishes Argo CD after EKS exists.

### Argo CD Owns

Argo CD owns Kubernetes runtime resources such as:

- application Deployments;
- Services;
- Ingress;
- migration Jobs;
- SecretProviderClass;
- AWS Load Balancer Controller.

This avoids overlapping control planes.

---

## 4. Infrastructure Principles

### 4.1 Infrastructure as Code Is Authoritative

AWS infrastructure changes should be represented in Terraform.

Manual resources discovered during implementation should either be:

- imported into Terraform;
- intentionally retained as an external dependency;
- removed when no longer required.

The Argo CD ECR repositories demonstrate this approach: they were created
during platform recovery work and later imported into Terraform ownership.

---

### 4.2 Drift Must Be Detectable

A clean environment should produce:

```text
No changes. Your infrastructure matches the configuration.
```

from:

```bash
terraform plan
```

Unexpected differences require investigation before a release or teardown.

---

### 4.3 Data Services Remain Private

RDS and Redis are not publicly exposed.

Application workloads reach them through private VPC networking and explicit
security-group relationships.

---

### 4.4 Public Access Terminates at the Edge

Public application traffic terminates at an AWS Application Load Balancer.

EKS worker nodes, PostgreSQL, and Redis do not require public addresses.

---

### 4.5 Least Privilege

Different identities exist for:

- EKS control plane;
- EKS worker nodes;
- application runtime;
- worker-specific operations;
- AWS Load Balancer Controller;
- Jenkins / CI delivery.

Applications do not inherit unrestricted node-role permissions.

---

### 4.6 Cost Is an Architectural Constraint

The development environment is intentionally temporary.

High-cost resources can be destroyed after validation and recreated when
required.

This makes recovery and rebuild capability part of the architecture rather
than optional operational documentation.

---

## 5. AWS Region

The current environment runs in:

```text
us-east-1
```

The region remains represented through Terraform configuration and outputs.

---

## 6. Terraform Repository Structure

Current Terraform structure:

```text
terraform/
├── bootstrap/
├── environments/
│   └── development/
│       ├── backend.tf
│       ├── main.tf
│       ├── outputs.tf
│       ├── providers.tf
│       ├── variables.tf
│       └── versions.tf
├── modules/
│   ├── application-runtime-iam/
│   ├── argocd-ecr/
│   ├── ci-delivery-iam/
│   ├── controller-ecr/
│   ├── ecr/
│   ├── eks/
│   ├── eks-workload-access/
│   ├── iam/
│   ├── load-balancer-controller-iam/
│   ├── networking/
│   ├── rds/
│   ├── redis/
│   ├── secrets/
│   ├── security-groups/
│   └── vpc-endpoints/
└── policies/
```

The environment layer composes reusable modules rather than declaring the
entire AWS platform as one monolithic configuration.

---

## 7. Environment Strategy

Supported environment names are designed around:

```text
development
staging
production
```

The current AWS implementation is the:

```text
development
```

environment.

Its purpose is:

- integration testing;
- Kubernetes validation;
- GitOps validation;
- platform engineering demonstrations;
- recovery testing;
- portfolio evidence collection.

The development environment favors cost-aware settings over full
production-level redundancy.

---

## 8. Terraform State

Terraform state is separated from application source state.

Remote state provides:

- shared state location;
- recovery capability;
- locking;
- reduced dependency on a single workstation.

Environment configuration lives under:

```text
terraform/environments/<environment>/
```

State separation prevents development infrastructure changes from implicitly
modifying another environment.

Terraform state files and sensitive variable files must not be committed to
Git.

---

## 9. Provider Strategy

Provider and Terraform versions are constrained in:

```text
versions.tf
```

and provider configuration is maintained independently in:

```text
providers.tf
```

Provider dependency lock files should remain committed so development and
automation consume reviewed provider versions.

Provider upgrades require:

1. configuration validation;
2. Terraform plan review;
3. resource replacement review;
4. application validation.

---

## 10. Naming Convention

The implemented naming pattern is:

```text
platform-launchpad-<environment>-<resource>
```

Examples:

```text
platform-launchpad-development-eks
platform-launchpad-development-postgres
platform-launchpad-development-redis
platform-launchpad-development-application
platform-launchpad-development-aws-load-balancer-controller
platform-launchpad-development-argocd
```

Terraform-managed resources also use environment and platform tags to improve
inventory and cost visibility.

---

## 11. VPC Architecture

The current platform VPC contains three network tiers:

```text
Public Subnets
      |
      v
Private Application Subnets
      |
      v
Private Database Subnets
```

The VPC spans multiple Availability Zones.

Terraform outputs expose:

```text
vpc_id
public_subnet_ids
private_app_subnet_ids
private_db_subnet_ids
```

---

## 12. Public Subnets

Public subnets contain edge and outbound-connectivity infrastructure.

Current responsibilities include:

- Application Load Balancer placement;
- NAT Gateway placement;
- Internet Gateway routing.

They carry Kubernetes subnet metadata required by AWS integrations.

Application worker nodes do not require placement in these public subnets.

---

## 13. Private Application Subnets

Private application subnets host the EKS worker nodes.

Kubernetes workloads running there include:

- frontend;
- backend;
- worker;
- Argo CD;
- AWS Load Balancer Controller;
- supporting cluster services.

These subnets have no direct Internet Gateway route.

Their external access is provided through controlled NAT egress or VPC
endpoints.

---

## 14. Private Database Subnets

Private database subnets host:

- Amazon RDS PostgreSQL;
- ElastiCache subnet placement.

They do not receive a general Internet default route.

This creates an additional network boundary between Kubernetes workloads and
persistent data services.

---

## 15. NAT Gateway

A NAT Gateway is implemented for private application subnet egress.

Terraform manages:

- Elastic IP;
- NAT Gateway;
- private application default route.

Conceptually:

```text
Private Application Subnets
        |
        | 0.0.0.0/0
        v
NAT Gateway
        |
        v
Internet Gateway
        |
        v
External Services
```

This became necessary because platform components such as Argo CD require
access to external Git repositories.

The NAT Gateway is one of the primary development cost drivers and should be
removed during teardown.

---

## 16. Database Route Isolation

The private database route table intentionally does not receive the NAT
default route.

This preserves the distinction:

```text
Application workloads:
    controlled outbound access

Database resources:
    private-only network placement
```

RDS and Redis do not require outbound public Internet connectivity for normal
application operations.

---

## 17. VPC Endpoints

The development environment uses VPC endpoints for selected AWS services.

Current Terraform outputs include endpoint identifiers for:

- Amazon EC2;
- Amazon ECR API;
- Amazon ECR Docker registry;
- Amazon EKS;
- EKS authentication;
- Elastic Load Balancing;
- AWS Secrets Manager;
- Amazon S3.

VPC endpoint benefits include:

- private access to AWS APIs;
- reduced dependency on NAT;
- improved network isolation;
- predictable AWS service routing.

Interface endpoints have their own cost, so endpoint selection remains a
balance between cost and network architecture.

---

## 18. Security Groups

Terraform separates security boundaries into dedicated security groups.

Important groups include:

```text
ALB security group
application security group
PostgreSQL security group
Redis security group
VPC endpoint security group
EKS cluster security group
```

### ALB

Permits public listener traffic required for:

```text
HTTP 80
HTTPS 443
```

### PostgreSQL

PostgreSQL ingress is restricted to the authorized application/EKS path on:

```text
TCP 5432
```

### Redis

Redis ingress is restricted to the authorized application/EKS path on:

```text
TCP 6379
```

Terraform explicitly manages EKS-to-database and EKS-to-Redis ingress rules.

---

## 19. Amazon EKS

The Kubernetes runtime is Amazon EKS.

Current cluster naming:

```text
platform-launchpad-development-eks
```

Terraform manages:

- cluster;
- cluster IAM role;
- managed node group;
- worker-node IAM;
- cluster access;
- required EKS addons;
- Pod Identity support;
- networking inputs.

The cluster is not treated as a manually configured resource.

---

## 20. EKS Managed Node Group

The primary managed node group is:

```text
platform-launchpad-development-primary
```

The validated development configuration uses:

```text
min     = 2
desired = 2
max     = 3
```

and currently uses cost-conscious EC2 worker instances.

Two nodes have been validated across separate Availability Zones.

This provides a meaningful availability demonstration without attempting to
model a large production cluster.

---

## 21. EKS Access

Administrative cluster access is explicitly configured rather than depending
only on legacy implicit behavior.

Operational identities and workload identities are intentionally separate.

Jenkins does not require unrestricted Kubernetes administrative credentials.

---

## 22. EKS Pod Identity

The implemented architecture uses **EKS Pod Identity**, not the earlier
planned IRSA-only model.

Pod Identity associations currently include application identities such as:

```text
backend
worker
aws-load-balancer-controller
```

This allows Kubernetes ServiceAccounts to assume narrowly scoped AWS roles
without embedding long-lived AWS access keys into containers.

---

## 23. Application Runtime IAM

The application runtime IAM module provides AWS access needed by backend and
worker ServiceAccounts.

Terraform manages:

- runtime IAM role;
- Secrets Manager access policy;
- policy attachment;
- Pod Identity associations.

The policy grants access to the runtime application secret rather than broad
Secrets Manager permissions.

---

## 24. Worker IAM

The worker retains a distinct IAM role and policy for worker-specific platform
operations.

This allows future worker responsibilities to expand independently without
granting equivalent permissions to the frontend or backend.

---

## 25. CI Delivery IAM

Terraform manages dedicated CI delivery identities.

The CI model separates:

```text
Jenkins identity
        |
        v
Assume CI delivery role
        |
        v
Approved ECR / delivery actions
```

Terraform outputs include:

- Jenkins user identity;
- role name;
- role ARN;
- ECR publication policy;
- assume-role policy.

CI credentials therefore do not need to provide unrestricted AWS
administrative access.

---

## 26. AWS Load Balancer Controller IAM

Terraform manages IAM prerequisites for the AWS Load Balancer Controller.

Resources include:

- controller IAM role;
- controller policy;
- policy attachment;
- EKS Pod Identity association.

Argo CD manages the Kubernetes Helm release while Terraform manages its AWS
identity prerequisites.

This preserves a clean ownership boundary.

---

## 27. Amazon ECR

Platform Launchpad uses private Amazon ECR repositories.

### Application Repository

The application repository stores the application container artifacts used by:

- backend;
- frontend;
- worker.

GitOps overlays deploy immutable image digests.

### AWS Load Balancer Controller Repository

The controller image is mirrored into:

```text
platform-launchpad-development-aws-load-balancer-controller
```

The runtime does not depend directly on the upstream public container
registry.

---

## 28. Argo CD Bootstrap ECR

Terraform owns three private repositories required by the Argo CD bootstrap:

```text
platform-launchpad-development-argocd
platform-launchpad-development-argocd-dex
platform-launchpad-development-argocd-redis
```

These repositories contain pinned private copies of:

```text
Argo CD
Dex
Redis
```

The repositories were originally created during runtime recovery work and
were later imported into Terraform state.

This demonstrates the project's rule that manually discovered infrastructure
must either be imported into IaC ownership or intentionally documented as
external.

---

## 29. ECR Lifecycle Management

Terraform applies lifecycle policies to managed repositories.

Lifecycle policies control retained image count and reduce unbounded storage
growth.

Image-retention policy must still preserve images required for:

- current deployment;
- rollback;
- bootstrap;
- recent known-good releases.

---

## 30. Amazon RDS PostgreSQL

Amazon RDS PostgreSQL is the production-style system of record.

Terraform manages:

- DB instance;
- DB subnet group;
- database security controls;
- storage configuration;
- database name;
- credential integration.

Current database naming follows:

```text
platform-launchpad-development-postgres
```

The application database name is:

```text
platform_launchpad
```

RDS is private and reachable from authorized Kubernetes workloads.

---

## 31. RDS Credentials

The RDS master password is generated and maintained through AWS-managed secret
integration rather than stored directly in source control.

Terraform exposes the secret ARN as an output for controlled operational use.

The application itself does not use the raw Terraform output as its runtime
configuration.

Instead, runtime application connection information is stored separately in
the application runtime secret.

---

## 32. Application Runtime Secret

Terraform manages:

```text
platform-launchpad/development/runtime
```

The current runtime secret contains:

```text
database_url
secret_key
```

The secret value is consumed in Kubernetes through the Secrets Store CSI
Driver.

Terraform manages the secret container and IAM authorization boundary.

Sensitive values themselves must never be committed to Git or Terraform
outputs intended for routine display.

---

## 33. ElastiCache Redis

Terraform provisions an ElastiCache Redis replication group.

Redis runs in private networking and uses a restricted security group.

Terraform exposes:

```text
redis_endpoint
redis_port
redis_replication_group_arn
```

Network connectivity from EKS to Redis has been validated.

The current application worker does not require Redis as its primary
deployment-request queue; Redis remains available for future caching,
coordination, or queue use cases.

---

## 34. Workload-to-Data Network Access

Terraform explicitly manages network rules allowing EKS workloads to reach:

```text
PostgreSQL :5432
Redis      :6379
```

This avoids broad CIDR-based ingress where a tighter security-group
relationship can be used.

Connectivity from Kubernetes workloads to both data services has been
validated.

---

## 35. Application Load Balancer Integration

Terraform manages AWS prerequisites such as:

- networking;
- security groups;
- controller IAM.

The Kubernetes Ingress and controller runtime are GitOps-managed.

The ALB therefore demonstrates shared responsibility:

```text
Terraform:
    AWS prerequisites

Argo CD:
    controller runtime
    Ingress desired state

AWS Load Balancer Controller:
    ALB reconciliation
```

---

## 36. Route 53 Ownership Boundary

The `christineadelusi.com` hosted zone currently exists in a separate AWS
development account.

The public record:

```text
launchpad.christineadelusi.com
```

points to the Platform Launchpad ALB.

This Route 53 record is currently an external/cross-account integration
dependency rather than a Terraform-managed resource in this environment.

That distinction must remain explicit in infrastructure documentation.

---

## 37. ACM Ownership Boundary

The Platform Launchpad TLS certificate exists in the AWS runtime account and
is consumed by the Kubernetes Ingress through the AWS Load Balancer
Controller.

ACM certificate creation is not currently represented by an output from the
development Terraform configuration.

It should therefore not be described as fully Terraform-owned until that
resource is added or imported into the infrastructure configuration.

---

## 38. Terraform Outputs

The development environment exposes operational outputs required by adjacent
platform layers.

Categories include:

### Networking

```text
vpc_id
public_subnet_ids
private_app_subnet_ids
private_db_subnet_ids
nat_gateway_id
nat_gateway_public_ip
```

### EKS

```text
eks_cluster_name
eks_cluster_arn
eks_cluster_endpoint
eks_cluster_version
eks_node_group_name
eks_node_group_status
```

### Data

```text
rds_endpoint
rds_instance_arn
redis_endpoint
redis_port
redis_replication_group_arn
```

### ECR

```text
ecr_repository_name
ecr_repository_url
load_balancer_controller_repository_url
argocd_repository_names
argocd_repository_urls
```

### Secrets

```text
runtime_secret_name
runtime_secret_arn
rds_master_user_secret_arn
```

### IAM and Pod Identity

```text
application_runtime_role_arn
application_runtime_policy_arn
application_runtime_pod_identity_association_ids
worker_role_arn
worker_policy_arn
load_balancer_controller_role_arn
ci_delivery_role_arn
```

### VPC Endpoints

Terraform also exposes endpoint identifiers for validation and troubleshooting.

Outputs form an API between Terraform and platform automation.

The Argo CD bootstrap intentionally consumes Terraform outputs instead of
hard-coding infrastructure identifiers.

---

## 39. Terraform-to-Bootstrap Integration

The Argo CD bootstrap script reads Terraform outputs such as:

```text
aws_region
eks_cluster_name
argocd_repository_urls
```

This creates a direct dependency chain:

```text
Terraform
    |
    | outputs
    v
Bootstrap Automation
    |
    v
Argo CD
```

The bootstrap script therefore remains portable across recreated
infrastructure without embedding cluster-specific IDs.

---

## 40. GitOps Boundary

Terraform does not deploy application Kubernetes manifests.

Argo CD owns those resources from the GitOps repository.

Likewise, Argo CD does not create the underlying VPC, EKS cluster, RDS
instance, Redis cluster, or IAM foundation.

This prevents Terraform and Argo CD from competing for ownership of the same
resources.

---

## 41. Validation Workflow

Infrastructure changes follow:

```text
terraform fmt
        |
        v
terraform validate
        |
        v
terraform plan
        |
        v
Plan inspection
        |
        v
terraform apply
        |
        v
Runtime validation
        |
        v
terraform plan
        |
        v
Zero drift
```

For higher-risk changes, plans are saved:

```bash
terraform plan -out=<plan-file>
```

and inspected before application.

---

## 42. Import Strategy

Infrastructure discovered outside Terraform should not remain permanently
unmanaged.

Adoption workflow:

```text
Existing AWS resource
        |
        v
Terraform configuration created
        |
        v
terraform import
        |
        v
terraform plan
        |
        v
Reconcile safe differences
        |
        v
Terraform ownership
```

The Argo CD ECR repositories are a validated example of this workflow.

---

## 43. Replacement Safety

Terraform plans must be reviewed specifically for:

```text
create
update
replace
destroy
```

Unexpected replacement of resources such as:

- RDS;
- EKS;
- VPC;
- NAT;
- IAM roles

must block an automatic apply until reviewed.

Saved plans are preferred for infrastructure changes where exact execution
matters.

---

## 44. Cost Management

The primary AWS development cost drivers include:

- EKS control plane;
- EC2 EKS worker nodes;
- NAT Gateway;
- RDS PostgreSQL;
- ElastiCache Redis;
- Application Load Balancer;
- interface VPC endpoints.

The environment should not remain running indefinitely after evidence
collection.

Cost control relies heavily on:

- temporary environment lifetime;
- small development instance sizes;
- minimal replica counts;
- controlled backup retention;
- lifecycle policies;
- deliberate teardown.

---

## 45. Development Teardown Philosophy

The development environment is designed to be disposable at the infrastructure
layer.

The expected lifecycle is:

```text
Provision
    |
    v
Validate
    |
    v
Demonstrate
    |
    v
Capture Evidence
    |
    v
Destroy
```

Source-controlled configuration remains available after teardown.

The ability to recreate the platform is considered more valuable than keeping
an idle demonstration environment running permanently.

---

## 46. Pre-Destroy Validation

Before destroying the environment:

1. ensure Git working trees are clean;
2. push all infrastructure changes;
3. record current Terraform outputs if useful;
4. capture architecture and application screenshots;
5. confirm Argo CD Applications are healthy;
6. capture deployment validation evidence;
7. decide whether database snapshots must be retained;
8. review external Route 53 records;
9. review external ACM resources;
10. inspect Terraform destroy plan.

A separate teardown runbook should document the exact operational sequence.

---

## 47. Rebuild Strategy

Rebuilding the development platform follows:

```text
Terraform
    |
    v
AWS infrastructure
    |
    v
Argo CD bootstrap
    |
    v
GitOps Applications
    |
    v
Database migration
    |
    v
Application runtime
```

Representative commands:

```bash
cd terraform/environments/development

terraform init
terraform plan
terraform apply
```

then:

```bash
cd ../../..

./bootstrap/argocd/install.sh
./bootstrap/argocd/apply-applications.sh
```

Argo CD then resumes Kubernetes reconciliation.

---

## 48. Recovery Design

The architecture reduces recovery dependence on individual machines.

Recovery assets include:

- Git repository;
- Terraform configuration;
- remote Terraform state;
- application source;
- GitOps repository;
- private container artifacts;
- bootstrap automation;
- database backup strategy;
- architecture documentation.

A failed Kubernetes cluster should therefore not require manual recreation of
application manifests.

---

## 49. Implemented vs External vs Planned

### Implemented and Terraform-Managed

```text
VPC
Subnets
Route tables
Internet Gateway
NAT Gateway
Security groups
EKS
Managed node group
EKS access
Pod Identity support
Application runtime IAM
Worker IAM
CI delivery IAM
AWS Load Balancer Controller IAM
Application ECR
Controller ECR
Argo CD ECR repositories
RDS PostgreSQL
ElastiCache Redis
Secrets Manager runtime secret
VPC endpoints
EKS-to-RDS rules
EKS-to-Redis rules
```

### Implemented but Managed Outside This Terraform Environment

```text
Route 53 public hosted zone
launchpad DNS record
ACM certificate
Argo CD Kubernetes runtime
AWS Load Balancer Controller Kubernetes runtime
Application Kubernetes resources
```

### Planned / Future

```text
Full staging AWS environment
Full production AWS environment
Terraform-managed cross-account DNS
Terraform-managed ACM lifecycle
observability infrastructure
autoscaling validation
budget alarms
additional backup automation
```

---

## 50. Infrastructure Evolution

The infrastructure evolved substantially from the original design.

### NAT

**Original design:** NAT was a production-style option with possible
cost-optimized alternatives.

**Implemented design:** a NAT Gateway was required for private workloads that
need external Git and Internet connectivity.

### EKS Workload Identity

**Original design:** IRSA was the expected mechanism.

**Implemented design:** EKS Pod Identity is used for the current runtime.

### Argo CD Registry Dependencies

**Original design:** Argo CD bootstrap registries were not explicitly modeled.

**Implemented design:** Argo CD, Dex, and Redis bootstrap images are mirrored
into Terraform-managed private ECR repositories.

### Platform Controller

**Original design:** AWS Load Balancer Controller was listed as an EKS
component.

**Implemented design:** AWS prerequisites are Terraform-managed while its
Kubernetes Helm deployment is Argo CD-managed.

### Secrets

**Original design:** Secrets Manager integration was planned.

**Implemented design:** the runtime secret and workload permissions are
Terraform-managed, while Kubernetes mounts values through Secrets Store CSI.

### Network Access

**Original design:** VPC endpoints were optional.

**Implemented design:** multiple endpoints are deployed alongside NAT egress
to provide private AWS service access.

---

## 51. Architecture Principles Demonstrated

The Terraform implementation demonstrates:

- modular Infrastructure as Code;
- environment-specific composition;
- private workload placement;
- private data tiers;
- controlled Internet egress;
- workload identity;
- least-privilege IAM;
- explicit security-group relationships;
- private artifact delivery;
- reusable Terraform outputs;
- infrastructure import and adoption;
- drift detection;
- GitOps ownership boundaries;
- bootstrap dependency management;
- cost-conscious architecture;
- deterministic recovery.

---

## 52. Summary

Terraform provides the AWS foundation for Platform Launchpad.

The current development implementation includes:

```text
Networking
EKS
IAM
Pod Identity
ECR
RDS
Redis
Secrets Manager
VPC Endpoints
NAT
Security Groups
```

Terraform intentionally stops at the cloud infrastructure boundary.

Argo CD owns Kubernetes desired state.

Bootstrap automation connects those two layers.

The resulting model is:

```text
Terraform
    |
    v
AWS Foundation
    |
    v
Argo CD Bootstrap
    |
    v
GitOps
    |
    v
Platform Runtime
```

This creates an infrastructure platform that is reproducible, auditable,
cost-aware, and suitable for controlled teardown and rebuild.