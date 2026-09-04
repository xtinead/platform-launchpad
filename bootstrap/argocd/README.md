# Argo CD Bootstrap

This directory contains the deterministic bootstrap process used to install
Argo CD and register the initial GitOps applications for Platform Launchpad.

The bootstrap layer exists to solve the initial GitOps dependency problem:
Argo CD cannot manage workloads from Git until Argo CD itself exists.

After bootstrap completes, Argo CD becomes the declarative delivery control
plane for the platform.

---

## Architecture

The platform uses three distinct ownership layers:

```text
Terraform
    |
    | provisions AWS infrastructure
    v
AWS Platform
    |
    | EKS, IAM, networking, ECR,
    | Secrets Manager, VPC endpoints
    v
Argo CD Bootstrap
    |
    | installs Argo CD from pinned
    | private-ECR runtime images
    v
Argo CD
    |
    | registers and reconciles GitOps applications
    v
+--------------------------------------+
| AWS Load Balancer Controller         |
| Platform Launchpad                   |
| Database migration hook              |
| Backend / Worker / Frontend          |
+--------------------------------------+
```

### Terraform owns

Terraform provisions the AWS infrastructure required before Kubernetes
workloads can be deployed, including:

- VPC networking
- public and private subnets
- NAT egress
- route tables
- Amazon EKS
- IAM roles and policies
- Amazon ECR repositories
- AWS Secrets Manager resources
- VPC endpoints
- supporting platform infrastructure

Terraform also owns the private ECR repositories used by the Argo CD
bootstrap process.

### Bootstrap owns

The bootstrap layer handles the minimum imperative work required to establish
the GitOps control plane:

1. validate local prerequisites;
2. validate AWS identity;
3. configure access to the EKS cluster;
4. authenticate Docker to private ECR;
5. mirror pinned Argo CD runtime images into private ECR;
6. download the pinned upstream Argo CD installation manifest;
7. rewrite public runtime image references to private ECR;
8. install or reconcile Argo CD;
9. verify the Argo CD workloads and CRDs;
10. register the initial Argo CD Applications.

### Argo CD owns

After bootstrap, Argo CD manages the declarative Kubernetes delivery layer,
including:

- AWS Load Balancer Controller;
- Platform Launchpad application resources;
- database migration execution through the Argo CD Sync hook;
- backend deployment and service;
- worker deployment;
- frontend deployment and service;
- ingress;
- runtime Kubernetes resources represented in the GitOps repository.

---

## Directory Contents

```text
bootstrap/argocd/
├── README.md
├── images.env
├── install.sh
├── rewrite_manifest.py
└── apply-applications.sh
```

### `images.env`

Defines the pinned versions and upstream locations of the runtime images used
by the Argo CD installation.

Current pinned versions:

| Component | Version |
| --- | --- |
| Argo CD | `v3.5.2` |
| Dex | `v2.45.1` |
| Redis | `8.2.3-alpine` |

Pinning these versions makes the bootstrap process reproducible and prevents a
rebuild from silently consuming newer upstream releases.

### `install.sh`

Bootstraps the Argo CD control plane.

The script:

- reads infrastructure information from Terraform outputs;
- validates required local commands;
- validates AWS identity;
- updates kubeconfig for the EKS cluster;
- authenticates Docker to private ECR;
- checks whether pinned images already exist in ECR;
- mirrors missing images when required;
- downloads the pinned Argo CD manifest;
- rewrites public image references;
- installs Argo CD using server-side apply;
- waits for Argo CD workloads to become available;
- verifies required Argo CD CRDs;
- verifies that running Argo CD workloads use private ECR images.

### `rewrite_manifest.py`

Rewrites the pinned upstream Argo CD installation manifest so that runtime
images are loaded from the platform's private ECR repositories rather than
directly from public registries.

The helper also fails when an expected upstream image reference is missing.
This protects the bootstrap process from silently accepting an unexpected
change in the upstream manifest.

### `apply-applications.sh`

Registers the initial Argo CD Application resources after the Argo CD control
plane is available.

The current bootstrap Applications are:

- `aws-load-balancer-controller-development`
- `platform-launchpad-development`

The Application definitions remain in the separate
`platform-launchpad-gitops` repository. The bootstrap script does not duplicate
their Kubernetes manifests.

---

## Prerequisites

The following tools must be available before running the bootstrap process:

- AWS CLI
- Terraform
- kubectl
- Docker
- curl
- Python
- Git

The AWS infrastructure must already have been provisioned with Terraform.

The operator must also have AWS permissions required to:

- access the EKS cluster;
- authenticate to ECR;
- inspect ECR images;
- push bootstrap images when they are not already present.

The Platform Launchpad GitOps repository must be available alongside the main
repository when registering Applications.

Expected local layout:

```text
apps/
├── platform-launchpad/
└── platform-launchpad-gitops/
```

---

## Bootstrap Sequence

### 1. Provision AWS infrastructure

From the appropriate Terraform environment:

```bash
cd terraform/environments/development

terraform init
terraform plan
terraform apply
```

Return to the repository root:

```bash
cd ../../..
```

### 2. Install Argo CD

Run:

```bash
./bootstrap/argocd/install.sh
```

The installation script is designed to be safe to rerun.

If the pinned runtime images already exist in ECR, the script reuses them
rather than unnecessarily pulling and pushing them again.

### 3. Register GitOps Applications

Run:

```bash
./bootstrap/argocd/apply-applications.sh
```

The script waits for the Argo CD Application CRD and then applies the initial
Application manifests from the GitOps repository.

Existing Applications are reconciled rather than duplicated.

---

## Validation

### Verify Argo CD

```bash
kubectl get pods \
  -n argocd
```

All Argo CD workloads should be healthy.

Verify the required CRDs:

```bash
kubectl get crd \
  applications.argoproj.io \
  applicationsets.argoproj.io \
  appprojects.argoproj.io
```

### Verify private runtime images

```bash
kubectl get pods \
  -n argocd \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{range .spec.initContainers[*]}  init: {.image}{"\n"}{end}{range .spec.containers[*]}  container: {.image}{"\n"}{end}{"\n"}{end}'
```

Argo CD, Dex, and Redis should reference the platform's private ECR
repositories.

### Verify Applications

```bash
kubectl get applications \
  -n argocd
```

Expected Applications:

```text
aws-load-balancer-controller-development
platform-launchpad-development
```

Once synchronized, both should report:

```text
SYNC STATUS     Synced
HEALTH STATUS   Healthy
```

### Verify Platform Launchpad

```bash
kubectl get pods \
  -n platform-launchpad
```

Expected application workloads:

```text
backend
frontend
worker
```

Verify backend readiness:

```bash
curl -sS \
  https://launchpad.christineadelusi.com/health/ready
```

Expected response:

```json
{"status":"ready","checks":{"database":"ok"}}
```

Verify the public frontend:

```bash
curl -I \
  https://launchpad.christineadelusi.com/
```

A healthy deployment should return an HTTP success response.

---

## Idempotency

Both bootstrap stages are designed to be rerunnable.

### Argo CD installation

`install.sh`:

- reuses existing private ECR images;
- applies the same pinned manifest;
- reconciles existing Kubernetes resources;
- waits for workloads to become healthy;
- validates the resulting runtime.

### Application registration

`apply-applications.sh` uses declarative Kubernetes apply semantics.

When the Application resources already match Git:

```text
application.argoproj.io/aws-load-balancer-controller-development unchanged
application.argoproj.io/platform-launchpad-development unchanged
```

This allows the bootstrap process to be rerun without recreating healthy
applications.

---

## GitOps Boundary

Argo CD itself is intentionally not bootstrapped by an Argo CD Application.

This avoids a circular dependency:

```text
Argo CD required
      |
      v
Application required to install Argo CD
      |
      v
Argo CD required to process Application
```

Instead:

```text
Terraform
    |
    v
Bootstrap Argo CD
    |
    v
Register Applications
    |
    v
Argo CD assumes GitOps ownership
```

This creates an explicit and recoverable bootstrap boundary.

The bootstrap scripts establish the control plane. The GitOps repository
defines the desired Kubernetes application state.

---

## Database Migrations

Platform Launchpad database migrations are executed through an Argo CD Sync
hook before application workloads are reconciled.

The migration Job runs:

```text
alembic upgrade head
```

and uses the same runtime secret mechanism and backend service account as the
application.

The migration hook runs before the normal application resources through its
negative sync wave.

A failed migration therefore prevents the deployment from proceeding as a
successful GitOps synchronization.

---

## Runtime Secrets

Runtime application secrets are not committed to Git.

Platform Launchpad uses:

```text
AWS Secrets Manager
        |
        v
Secrets Store CSI Driver
        |
        v
SecretProviderClass
        |
        v
Backend / Worker / Migration Job
```

The application consumes secret values through mounted files rather than
embedding credentials directly in Kubernetes manifests.

---

## Recovery Model

For a fresh platform rebuild, the intended sequence is:

```text
1. terraform apply
2. ./bootstrap/argocd/install.sh
3. ./bootstrap/argocd/apply-applications.sh
4. synchronize the registered Argo CD Applications
5. verify platform health
```

This separates infrastructure provisioning, GitOps control-plane bootstrap,
and application reconciliation into clear operational boundaries.

---

## Design Goals

The bootstrap implementation is designed around the following platform
engineering principles:

- reproducible infrastructure;
- pinned software versions;
- private runtime artifact consumption;
- explicit ownership boundaries;
- least manual intervention;
- idempotent recovery operations;
- Git-based desired state;
- observable failure points;
- deterministic rebuild procedures.

The goal is not to eliminate bootstrap logic entirely. The goal is to keep the
imperative bootstrap surface small, deterministic, auditable, and easy to
recover.