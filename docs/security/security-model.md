# Platform Launchpad — Security Model

## 1. Purpose

This document defines the security architecture and implemented security
controls for Platform Launchpad.

Platform Launchpad is a production-style platform engineering portfolio
application deployed to AWS and Amazon EKS. Security is enforced across the
application, CI/CD, infrastructure, Kubernetes, GitOps, data, identity, and
network layers.

The security model is based on the following principles:

- least privilege;
- defense in depth;
- explicit trust boundaries;
- private-by-default infrastructure;
- secrets outside source control;
- immutable application delivery;
- separation of CI and CD responsibilities;
- declarative infrastructure and runtime state;
- auditable administrative and deployment activity;
- reproducible recovery;
- controlled exposure of public services.

This document describes both application-level security requirements and the
security controls implemented in the AWS development environment.

---

## 2. Current Security Posture

The development environment has been deployed and validated on AWS.

Implemented security controls include:

- application workloads running on Amazon EKS;
- application workloads placed in private subnets;
- Amazon RDS deployed without public accessibility;
- Redis deployed within private networking;
- AWS Secrets Manager used as the authoritative runtime secret store;
- Secrets Store CSI Driver used to mount application secrets into Kubernetes;
- EKS Pod Identity used for workload access to AWS services;
- dedicated Kubernetes service accounts;
- private Amazon ECR repositories;
- immutable application image digests in GitOps manifests;
- non-root application containers;
- privilege escalation disabled;
- Linux capabilities dropped where supported;
- read-only root filesystems where supported;
- Kubernetes readiness and liveness probes;
- AWS Application Load Balancer ingress;
- AWS Certificate Manager TLS certificate;
- HTTP-to-HTTPS redirection;
- AWS Load Balancer Controller using least-privilege AWS identity;
- Jenkins separated from Kubernetes runtime reconciliation;
- Argo CD acting as the Kubernetes reconciliation authority;
- Terraform acting as the AWS infrastructure provisioning authority;
- remote Terraform state protection;
- private Argo CD bootstrap image mirrors in ECR;
- pinned Argo CD bootstrap component versions;
- database migrations executed as an Argo CD Sync hook;
- infrastructure drift validation through Terraform;
- GitOps reconciliation validation through Argo CD.

The development environment is intentionally temporary and can be destroyed
after validation to reduce cloud cost. Security-sensitive state required for
reconstruction is represented through Terraform, Git, GitOps configuration,
and approved secret-management mechanisms rather than through undocumented
manual configuration.

---

## 3. Security Principles

### 3.1 Least Privilege

Every identity receives only the permissions required for its responsibility.

This applies to:

- application users;
- administrators;
- Jenkins;
- Terraform;
- EKS nodes;
- Kubernetes service accounts;
- application workloads;
- AWS Load Balancer Controller;
- Argo CD;
- database identities.

Broad administrative permissions are not considered an acceptable steady-state
runtime configuration.

### 3.2 Defense in Depth

No single control is treated as sufficient.

Security boundaries are implemented across:

```text
Browser
   |
   v
HTTPS / ALB
   |
   v
Kubernetes Ingress
   |
   v
Frontend
   |
   v
Backend Authorization
   |
   +------> PostgreSQL
   |
   +------> Runtime AWS Services

GitHub
   |
   v
Jenkins
   |
   +------> Private ECR
   |
   +------> GitOps Repository
                  |
                  v
               Argo CD
                  |
                  v
              Kubernetes
```

Application authorization, AWS IAM, Kubernetes RBAC, security groups, private
networking, secret management, and Git review all contribute independent
controls.

### 3.3 Secure Defaults

Resources should be private unless public exposure is explicitly required.

Examples include:

- RDS is private;
- Redis is private;
- EKS application workloads use private subnets;
- public traffic enters through the ALB;
- secrets are stored outside Git;
- AWS access uses roles and workload identity;
- runtime containers avoid privileged execution.

### 3.4 Secrets Never Enter Source Control

The following must never be committed:

- passwords;
- JWT signing secrets;
- database credentials;
- Redis credentials;
- AWS access keys;
- GitHub tokens;
- Jenkins credentials;
- Argo CD administrative credentials;
- Kubernetes credentials;
- TLS private keys;
- Terraform state containing sensitive values.

Safe placeholders may be committed where documentation requires examples.

### 3.5 GitOps Is the Runtime Deployment Authority

Kubernetes application state is managed through Git and Argo CD.

Jenkins does not require unrestricted Kubernetes deployment access.

This separation reduces the blast radius of a compromised CI system and
preserves an auditable deployment history.

### 3.6 Terraform Is the Infrastructure Authority

Terraform is authoritative for the AWS infrastructure represented in the
development environment.

Infrastructure changes should be:

1. represented in Terraform;
2. reviewed;
3. planned;
4. applied deliberately;
5. validated for drift.

Manual infrastructure changes should not become undocumented persistent state.

---

## 4. Security Assets

Assets requiring protection include:

### Identity Data

- user accounts;
- password hashes;
- roles;
- account status;
- authentication state.

### Application Data

- environment records;
- deployment requests;
- audit records;
- lifecycle history.

### Credentials and Secrets

- JWT signing secret;
- PostgreSQL credentials;
- Redis credentials where applicable;
- AWS IAM trust relationships;
- Jenkins credentials;
- GitHub credentials;
- Argo CD credentials;
- TLS private keys.

### Infrastructure

- EKS cluster;
- RDS database;
- Redis;
- ECR repositories;
- VPC;
- subnets;
- security groups;
- Route 53 records;
- ACM certificates;
- Terraform state;
- Kubernetes namespaces and workloads.

### Delivery Systems

- application repository;
- GitOps repository;
- Jenkins pipeline;
- Argo CD;
- Terraform configuration.

---

## 5. Trust Boundaries

Primary trust boundaries are:

1. Browser to public ALB
2. ALB to Kubernetes workloads
3. Frontend to backend API
4. Backend to PostgreSQL
5. Application workloads to AWS services
6. Jenkins to AWS
7. Jenkins to GitHub
8. Argo CD to GitHub
9. Argo CD to Kubernetes API
10. Kubernetes workloads to AWS through EKS Pod Identity
11. Terraform operator or automation to AWS APIs
12. AWS Secrets Manager to Kubernetes through the CSI integration

Each boundary requires explicit authentication, authorization, network
restriction, or cryptographic protection appropriate to the interaction.

---

## 6. Authentication

Platform Launchpad uses application authentication to establish user identity.

Passwords must:

- never be stored in plaintext;
- be processed through a maintained password-hashing implementation;
- never be logged;
- never appear in audit records;
- never be returned by the API.

Authentication responses must avoid leaking whether sensitive internal state
exists.

The application must reject disabled users.

Future production hardening may include:

- MFA;
- refresh-token rotation;
- centralized identity federation;
- stronger session revocation.

---

## 7. JWT Security

JWTs are treated as credentials.

Requirements include:

- signing secrets remain outside source control;
- short-lived access tokens;
- HTTPS-only transmission in hosted environments;
- tokens are not logged;
- tokens are not placed in URLs;
- authorization decisions are performed server-side;
- disabled users cannot continue using previously issued credentials where
  application validation supports account-state enforcement.

Future iterations may introduce asymmetric signing, refresh-token rotation, or
external identity providers.

---

## 8. Authorization

The FastAPI backend is the authoritative application authorization boundary.

Authorization decisions must not rely on:

- frontend visibility;
- browser state;
- hidden fields;
- client-supplied role values;
- client-supplied ownership values.

Role and ownership checks are enforced by backend dependencies and application
logic.

---

## 9. Role-Based Access Control

Platform Launchpad supports role-aware application behavior.

Regular users may perform authorized actions against resources they own.

Administrative capabilities may include:

- viewing users;
- enabling or disabling users;
- viewing environments;
- reviewing failed deployment requests;
- retrying supported requests;
- reviewing audit logs;
- performing controlled status overrides.

### Ownership Enforcement

For environment-scoped operations, the backend verifies the equivalent of:

```text
environment.owner_id == current_user.id
```

or administrative authorization.

The frontend is not authoritative for ownership.

### Resource Concealment

Protected resources may return `404 Not Found` instead of `403 Forbidden`
where concealment reduces resource enumeration.

---

## 10. Account Security

Users have an active/inactive lifecycle state.

Disabled users must be prevented from:

- authenticating;
- using protected application functionality;
- creating environments;
- destroying environments;
- performing authenticated lifecycle operations.

Historical user records should be deactivated rather than physically removed
when deletion would break operational or audit history.

Administrative account-state changes should create audit events.

---

## 11. Input Validation

All externally supplied values are untrusted.

Validation includes:

- email format;
- string lengths;
- UUID format;
- enum values;
- environment-name format;
- pagination limits;
- supported lifecycle states;
- supported deployment operations.

The backend must not trust:

- frontend validation;
- hidden browser fields;
- user-provided administrative flags;
- user-provided owner IDs;
- user-provided lifecycle status.

Unknown fields should be rejected where practical.

---

## 12. Environment Name Security

Environment names may influence:

- Kubernetes resources;
- DNS names;
- GitOps paths;
- labels;
- cloud tags.

Names must therefore use a constrained format such as:

```text
^[a-z0-9][a-z0-9-]*[a-z0-9]$
```

User input must not be interpolated directly into unrestricted shell commands.

Infrastructure integrations should use structured APIs, declarative
configuration, or safely parameterized execution.

---

## 13. API Security

The FastAPI backend provides the principal application security boundary.

Controls include or should include:

- authentication dependencies;
- authorization dependencies;
- ownership enforcement;
- request validation;
- safe errors;
- correlation identifiers;
- controlled CORS;
- structured logging;
- health checks.

Public production hardening should additionally include appropriately tuned:

- rate limits;
- request-size controls;
- comprehensive response security headers.

The API must not expose:

- stack traces;
- raw database errors;
- credential values;
- signing secrets;
- sensitive SQL data;
- internal implementation details unnecessarily.

---

## 14. CORS

CORS uses an explicit allowlist appropriate to the environment.

Local development may permit:

```text
http://localhost:3000
```

Hosted environments should permit only approved application origins.

Credentialed browser requests must not rely on unrestricted wildcard origins.

---

## 15. CSRF Considerations

Bearer tokens transmitted through the `Authorization` header reduce exposure
to traditional cookie-based CSRF patterns but introduce token-storage
considerations.

If browser authentication moves to cookies, additional controls should include:

- `SameSite`;
- `Secure`;
- CSRF validation where required;
- origin validation for state-changing requests.

---

## 16. Rate Limiting

Rate limiting is an additional public-production hardening requirement.

High-value targets include:

- registration;
- login;
- environment creation;
- destructive lifecycle operations;
- administrative retries;
- administrative overrides.

Limits should consider both identity and source characteristics.

---

## 17. PostgreSQL and RDS Security

The AWS environment uses Amazon RDS as the application system of record.

Implemented infrastructure controls include:

- private database networking;
- no public RDS exposure;
- security-group-controlled access;
- encrypted storage;
- credentials stored through AWS Secrets Manager;
- application access from authorized workloads.

The application database identity should not be a PostgreSQL superuser.

Database secrets must not appear in:

- Git;
- GitOps manifests;
- container images;
- application logs;
- Jenkinsfiles.

Database migrations are executed through a controlled Argo CD Sync hook rather
than through ad hoc manual execution against the cluster.

Migration workloads use the same security principles as application workloads,
including controlled identity, secret access, and hardened container settings.

---

## 18. Redis Security

Redis is deployed as a private platform data service and is not publicly
exposed.

The current Platform Launchpad worker implementation uses **database-backed
polling for deployment requests**. Redis is therefore not the authoritative
deployment-request queue in the current architecture.

Redis remains available for bounded transient capabilities where appropriate.

Security requirements include:

- private networking;
- restricted security-group access;
- authentication where configured;
- encrypted transport where required by the target environment;
- no permanent authoritative application state;
- no secrets embedded in transient payloads.

---

## 19. Worker Security

The deployment worker processes persisted deployment requests using the
application database-backed polling model.

The worker must:

- process only valid persisted deployment requests;
- validate referenced environments and operations;
- enforce valid lifecycle transitions;
- use idempotent processing behavior;
- avoid unrestricted shell execution;
- sanitize failures;
- avoid logging secrets;
- use least-privilege AWS identity when AWS access is required;
- preserve lifecycle and audit information.

Application users must never be able to submit arbitrary Terraform,
Kubernetes, or shell programs for worker execution.

---

## 20. Audit Logging

Security-relevant events should produce audit records.

Examples include:

- registration;
- successful authentication;
- failed authentication;
- account enable/disable;
- environment creation;
- lifecycle requests;
- provisioning success/failure;
- destruction;
- administrative retry;
- administrative overrides;
- significant authorization failures.

Audit records must not contain:

- passwords;
- password hashes;
- JWTs;
- AWS credentials;
- database passwords;
- private keys;
- secret values;
- complete sensitive connection strings.

Audit records are append-oriented operational evidence.

---

## 21. Application Logging

Application logs should be structured and operationally useful.

Useful fields include:

- timestamp;
- severity;
- service;
- environment;
- request ID;
- trace ID;
- route;
- method;
- status;
- duration;
- deployment-request ID;
- environment ID.

Logs must exclude:

- authorization headers;
- credential cookies;
- passwords;
- JWT contents;
- secret values;
- sensitive request bodies.

---

## 22. Error Handling

Client-facing errors must be safe and predictable.

Production responses must not expose:

- Python tracebacks;
- SQLAlchemy internals;
- filesystem paths;
- AWS credentials;
- database credentials;
- secret values;
- unnecessary internal infrastructure details.

Detailed diagnostics belong in controlled server-side logs correlated through
request or trace identifiers.

---

## 23. Frontend Security

The Next.js frontend must:

- contain no server credentials in client bundles;
- treat browser input as untrusted;
- avoid unsafe HTML rendering;
- protect authenticated navigation;
- hide role-inappropriate controls;
- handle expired authentication state;
- avoid credentials in URLs;
- operate over HTTPS in AWS;
- use appropriate browser security headers.

Frontend authorization behavior is usability support, not the security
boundary. Backend authorization remains authoritative.

---

## 24. HTTP Security Headers

Public frontend and API responses should use appropriate browser controls,
including:

- Content Security Policy;
- Strict Transport Security;
- X-Content-Type-Options;
- Referrer-Policy;
- Permissions-Policy;
- framing restrictions.

The exact policy should be tested against actual frontend runtime requirements
before strict enforcement.

---

## 25. Dependency Security

Python, Node.js, container, Terraform, and Kubernetes dependencies should be:

- pinned or locked where practical;
- reviewed through source control;
- scanned;
- updated deliberately;
- removed when unnecessary.

Pipeline security checks should include appropriate combinations of:

- dependency scanning;
- static analysis;
- secret scanning;
- container scanning;
- infrastructure validation.

Critical findings should block promotion unless an explicit exception is
documented.

---

## 26. Container Security

Application images follow a hardened runtime model.

Controls include:

- trusted base images;
- explicit versions;
- private ECR publication;
- non-root execution;
- minimized runtime packages;
- multi-stage builds where appropriate;
- exclusion of `.env`;
- exclusion of Git metadata;
- readiness and liveness probes;
- immutable image digest references in GitOps;
- container scanning as part of delivery controls.

Kubernetes runtime security settings include where supported:

```yaml
allowPrivilegeEscalation: false
readOnlyRootFilesystem: true
runAsNonRoot: true
capabilities:
  drop:
    - ALL
```

Images must not contain:

- AWS credentials;
- database credentials;
- Jenkins credentials;
- GitHub tokens;
- kubeconfig files;
- private keys.

---

## 27. Jenkins Security and CI/CD Separation

Jenkins is the CI and artifact-publication system.

Its responsibilities include:

- checkout;
- tests;
- linting;
- static analysis;
- dependency validation;
- image build;
- image scanning;
- ECR publication;
- controlled GitOps repository updates.

Jenkins does **not** own runtime Kubernetes reconciliation.

The delivery boundary is:

```text
Jenkins
   |
   +---- build/test/scan
   |
   +---- publish immutable image --> ECR
   |
   +---- update desired state ----> GitOps repository
                                      |
                                      v
                                   Argo CD
                                      |
                                      v
                                  Kubernetes
```

Jenkins must not:

- hold unrestricted cluster-admin credentials;
- deploy normal application workloads directly with unrestricted `kubectl`;
- embed credentials in Jenkinsfiles;
- expose credentials in build logs;
- rely on long-lived IAM user keys when role-based access is available.

CI AWS permissions are separated through dedicated IAM configuration,
including the CI delivery role and ECR publication permissions.

---

## 28. Software Supply-Chain Security

The delivery process protects the transition from source code to running
container.

Controls include:

- controlled source repositories;
- reviewed changes;
- CI validation;
- private ECR repositories;
- immutable image digests;
- Git-based desired state;
- Argo CD reconciliation;
- Terraform-managed infrastructure.

Future hardening may include:

- SBOM generation;
- image signing;
- provenance attestations;
- signature verification;
- Kubernetes admission policies.

These are future enhancements and are not represented as currently deployed
controls.

---

## 29. GitHub Security

Source and GitOps repositories should use:

- protected primary branches;
- pull-request review;
- required CI checks where appropriate;
- restricted force pushes;
- secret scanning;
- dependency alerts;
- least-privilege credentials.

Security-sensitive changes deserve explicit review, especially:

- IAM;
- authentication;
- Terraform;
- Jenkins;
- Kubernetes security contexts;
- GitOps configuration;
- secrets integration.

Git history provides an important part of the platform's deployment and
configuration audit trail.

---

## 30. Terraform Security

Terraform is the AWS infrastructure authority.

Controls include:

- remote state;
- encrypted state storage;
- restricted state access;
- state locking;
- no committed `.tfstate`;
- no committed `.terraform` directory;
- reviewed plans;
- deliberate applies;
- least-privilege AWS execution identities;
- drift detection.

Terraform state is confidential because providers and resources may record
sensitive infrastructure metadata.

The platform has also used `terraform import` where pre-existing AWS resources
needed to be adopted into Terraform ownership rather than recreated.

Import is an ownership transition mechanism, not a substitute for declarative
configuration.

A clean Terraform plan is used as evidence that represented infrastructure
matches declared configuration.

---

## 31. AWS IAM and EKS Pod Identity

AWS access uses roles and workload identity rather than embedding long-lived
AWS credentials into application containers.

The current EKS architecture uses **EKS Pod Identity** for supported workload
access.

Implemented identity categories include:

- EKS cluster and node identities;
- application runtime identity;
- CI delivery identity;
- AWS Load Balancer Controller identity;
- secret-access permissions;
- EKS Pod Identity associations;
- ECR access permissions.

The application runtime role is associated with the appropriate Kubernetes
service account through EKS Pod Identity.

This allows pods to receive temporary AWS credentials without storing static
AWS access keys in:

- Git;
- Kubernetes manifests;
- container images;
- environment files;
- Jenkins configuration.

IAM policies should avoid:

```text
Action: "*"
Resource: "*"
```

except where an explicitly reviewed AWS API limitation or tightly bounded
bootstrap requirement makes broader scope unavoidable.

Earlier architecture concepts based primarily on IRSA have been superseded by
the implemented EKS Pod Identity model for the current application workloads.

---

## 32. AWS Network Security

The AWS network follows a layered public/private model.

Implemented controls include:

- VPC isolation;
- public subnets for internet-facing infrastructure where required;
- private application subnets;
- private database subnets;
- restricted security groups;
- no public RDS endpoint;
- controlled outbound access;
- NAT-based private-subnet egress where required;
- VPC endpoints for selected AWS services;
- ALB-controlled public ingress.

Traffic follows approximately:

```text
Internet
   |
   v
Public ALB
   |
   v
Private EKS Workloads
   |
   +------> Private RDS
   |
   +------> Private Redis
   |
   +------> AWS Services
```

Security groups should reference other security groups where practical rather
than unnecessarily broad CIDR ranges.

The NAT Gateway provides outbound connectivity and does not make private
workloads directly internet-addressable.

---

## 33. Kubernetes Security

Application workloads run in the dedicated:

```text
platform-launchpad
```

namespace.

Platform dependencies use their appropriate namespaces, including:

```text
argocd
kube-system
```

Workload controls include:

- dedicated service accounts;
- namespace separation;
- readiness probes;
- liveness probes;
- resource requests and limits where configured;
- non-root execution;
- privilege escalation disabled;
- Linux capabilities dropped;
- read-only root filesystem where supported;
- controlled secret mounts;
- immutable image digest references;
- AWS workload identity through EKS Pod Identity.

Application workloads should not rely on the default service account when AWS
or Kubernetes permissions require a dedicated identity.

Future hardening may add more restrictive:

- NetworkPolicy;
- admission policy;
- Pod Security Admission enforcement.

These should not be described as implemented until validated in the deployed
environment.

---

## 34. Argo CD Security

Argo CD is the Kubernetes runtime reconciliation authority.

It currently reconciles applications including:

```text
platform-launchpad-development
aws-load-balancer-controller-development
```

Security properties include:

- desired state stored in Git;
- deployment history preserved through Git commits;
- runtime reconciliation separated from Jenkins;
- approved repository configuration;
- namespace-aware application destinations;
- no plaintext runtime secrets committed to application manifests;
- controlled bootstrap;
- pinned bootstrap component versions;
- private ECR mirrors for required Argo CD runtime images.

The bootstrap process mirrors:

- Argo CD;
- Dex;
- Redis

into Terraform-managed private ECR repositories before installation.

The downloaded pinned Argo CD installation manifest is rewritten to reference
those private images and validated to ensure public runtime image references
are not retained.

Argo CD administrative credentials must never be committed to Git.

For longer-lived or production environments, stronger administrative access
controls such as enterprise SSO should be considered.

---

## 35. Secrets Management

### Local Development

Local development may use:

```text
.env
```

Requirements:

- `.env` remains ignored by Git;
- `.env.example` contains placeholders only;
- development credentials are not reused as hosted credentials.

### AWS Development Environment

AWS Secrets Manager is the authoritative store for application runtime
secrets.

Kubernetes integrates with Secrets Manager through the Secrets Store CSI
Driver.

The security flow is:

```text
AWS Secrets Manager
        |
        | IAM-authorized retrieval
        v
EKS Pod Identity
        |
        v
Secrets Store CSI Driver
        |
        v
Mounted Secret Files
        |
        v
Application Workload
```

This design avoids storing plaintext runtime secret values directly in GitOps
manifests.

Access to secrets is controlled through the workload's AWS identity and IAM
policy.

Applications must not log mounted secret contents.

Secret files should be readable only by the workload that requires them.

Rotation procedures should account for whether a workload must restart or
reload configuration after the underlying secret changes.

---

## 36. TLS and Public Ingress

Public Platform Launchpad traffic enters through an AWS Application Load
Balancer managed through Kubernetes ingress resources and the AWS Load
Balancer Controller.

The public application endpoint is:

```text
https://launchpad.christineadelusi.com
```

TLS is provided using AWS Certificate Manager.

Public HTTP traffic is redirected to HTTPS.

The trust path is:

```text
Browser
   |
   | HTTPS
   v
AWS Application Load Balancer
   |
   v
Kubernetes Ingress Routing
   |
   +------> Frontend
   |
   +------> Backend API
```

Sensitive credentials must never be intentionally transmitted over plaintext
public network connections.

### DNS and Certificate Ownership Boundary

The DNS zone and certificate lifecycle may cross Terraform ownership or AWS
account boundaries.

The platform therefore distinguishes between:

- infrastructure it creates;
- infrastructure it references;
- externally owned DNS or certificate resources.

Terraform must not accidentally destroy externally owned Route 53 zones or ACM
certificates during environment teardown.

---

## 37. AWS Load Balancer Controller Security

The AWS Load Balancer Controller is treated as a platform dependency rather
than an application component.

It is managed through Argo CD and runs in:

```text
kube-system
```

Its AWS permissions are provided through a dedicated least-privilege identity.

The controller may create and reconcile AWS load-balancing resources required
by approved Kubernetes ingress configuration.

Its permissions should not be shared with normal application workloads.

This separation limits the impact of an application workload compromise.

---

## 38. Database Migration Security

Schema migrations are automated through an Argo CD Sync hook.

This provides a controlled deployment sequence rather than requiring manual
database mutation during application rollout.

The migration job:

- runs from declarative GitOps configuration;
- uses an approved application image;
- receives database access through the same controlled secret-management
  architecture;
- runs with hardened Kubernetes security settings;
- completes before dependent application reconciliation proceeds where the
  configured hook ordering requires it.

Migration credentials should have only the database permissions necessary for
the migration strategy.

---

## 39. Private Container Registry Security

Platform Launchpad uses private Amazon ECR repositories for application and
selected platform images.

Controls include:

- Terraform-managed repositories;
- lifecycle policies;
- IAM-controlled push/pull permissions;
- CI publication through dedicated permissions;
- Kubernetes consumption from ECR;
- immutable application image digests in GitOps desired state.

Argo CD bootstrap dependencies are mirrored into dedicated private ECR
repositories to reduce runtime dependence on public container registries
during platform reconstruction.

Public upstream images are treated as build/bootstrap inputs rather than the
final intended private runtime source for the mirrored Argo CD components.

---

## 40. Threat Scenarios

### Credential Stuffing or Password Guessing

Controls include:

- password hashing;
- generic authentication failures;
- audit logging;
- planned rate limiting;
- future MFA.

### Horizontal Privilege Escalation

A user attempts to access another user's environment.

Controls:

- backend ownership checks;
- UUID identifiers;
- resource concealment;
- authorization tests.

UUIDs are identifiers, not authorization controls.

### Vertical Privilege Escalation

A user attempts to invoke administrative operations.

Controls:

- backend role enforcement;
- protected admin routes;
- audit logging;
- authorization tests.

### Secret Committed to Git

Controls:

- `.gitignore`;
- Secrets Manager;
- CSI-based secret delivery;
- secret scanning;
- review;
- rotation procedure.

### Compromised Jenkins

Controls:

- CI/CD separation;
- dedicated AWS permissions;
- no runtime reconciliation authority;
- no unrestricted cluster-admin credential requirement;
- GitOps changes remain visible in Git;
- Argo CD performs deployment reconciliation.

### Compromised Application Pod

Controls:

- private networking;
- non-root execution;
- dropped capabilities;
- restricted privilege escalation;
- read-only root filesystem where supported;
- dedicated service account;
- EKS Pod Identity;
- least-privilege IAM;
- restricted database network access.

### Malicious or Replaced Container Image

Controls:

- private ECR;
- CI scanning;
- controlled publication;
- immutable image digest references;
- Git-reviewed deployment state.

Future controls may include image signing and admission verification.

### Database Exposure

Controls:

- private RDS;
- restricted security groups;
- no public endpoint;
- encrypted storage;
- Secrets Manager credentials.

### Unauthorized Terraform Apply

Controls:

- protected source;
- plan review;
- restricted AWS identity;
- protected remote state;
- auditable Git history;
- drift validation.

### GitOps Repository Compromise

Controls:

- repository access control;
- branch protection;
- review;
- Git audit history;
- Argo CD scope;
- no plaintext runtime secrets in manifests.

### Public Registry Dependency During Bootstrap

Controls:

- pinned upstream versions;
- Terraform-managed private ECR mirrors;
- controlled mirroring;
- manifest rewriting;
- validation that public runtime image references have been removed.

---

## 41. Security Testing

Security validation includes application, infrastructure, and delivery
controls.

### Authentication

Test:

- successful registration;
- duplicate registration;
- weak passwords;
- successful login;
- invalid login;
- disabled users;
- expired tokens;
- invalid tokens.

### Authorization

Test:

- owner access;
- cross-user denial;
- admin restrictions;
- disabled-user behavior.

### Input

Test:

- invalid UUIDs;
- invalid environment names;
- unsupported operations;
- invalid lifecycle transitions;
- oversized fields;
- pagination limits.

### Platform

Validate:

```bash
terraform plan
```

Expected stable state:

```text
No changes.
```

Validate Argo CD:

```bash
kubectl get applications -n argocd
```

Expected applications should report:

```text
Synced
Healthy
```

Validate application pods:

```bash
kubectl get pods -n platform-launchpad
```

Validate public TLS:

```bash
curl -I https://launchpad.christineadelusi.com/
```

Validate application readiness:

```bash
curl -sS https://launchpad.christineadelusi.com/health/ready
```

The validated development environment has demonstrated successful application
responses, database readiness, worker processing, healthy GitOps
reconciliation, and zero Terraform drift.

---

## 42. Incident Response Expectations

A longer-lived production deployment should define formal procedures for:

- credential compromise;
- secret rotation;
- compromised application images;
- unauthorized IAM activity;
- compromised CI credentials;
- GitOps repository compromise;
- database compromise;
- suspicious authentication activity;
- infrastructure drift;
- certificate compromise.

The development portfolio environment emphasizes reproducibility, which also
supports incident recovery: infrastructure and workloads can be destroyed and
reconstructed from authoritative configuration rather than relying on
untracked manual state.

---

## 43. Teardown Security

Environment teardown is both a cost-control operation and a security
operation.

Before teardown:

1. confirm required evidence and documentation are preserved;
2. ensure source and GitOps repositories are pushed;
3. verify Terraform configuration represents the intended infrastructure;
4. verify no required secret exists only inside a temporary runtime resource;
5. identify externally owned Route 53 and ACM resources that must survive;
6. confirm state storage required for Terraform remains available.

During teardown:

- use Terraform for Terraform-owned AWS infrastructure;
- avoid manually deleting resources that Terraform still owns unless recovery
  requires it;
- verify load balancers and NAT resources are removed;
- verify temporary compute resources are removed;
- preserve intentionally external/shared resources.

After teardown:

- inspect Terraform state;
- inspect AWS for orphaned cost-generating resources;
- confirm sensitive temporary resources are gone;
- preserve only the resources intentionally required for rebuild.

---

## 44. Recovery Security

Reconstruction follows controlled trust establishment.

A high-level recovery sequence is:

```text
Terraform foundation
        |
        v
AWS infrastructure
        |
        v
EKS + IAM + ECR + Secrets prerequisites
        |
        v
Argo CD bootstrap
        |
        v
GitOps Application bootstrap
        |
        v
Argo CD reconciliation
        |
        v
Application workloads
        |
        v
Validation
```

The bootstrap process must not bypass security controls merely because the
cluster is being rebuilt.

Recovery should restore:

- identity boundaries;
- network boundaries;
- private registries;
- workload identity;
- secret delivery;
- TLS;
- GitOps reconciliation;
- hardened workload settings.

---

## 45. Security Ownership Boundaries

Platform Launchpad deliberately separates authority.

| Layer | Primary Authority |
|---|---|
| Application authentication | FastAPI |
| Application authorization | FastAPI |
| User/environment state | PostgreSQL |
| Runtime secrets | AWS Secrets Manager |
| AWS infrastructure | Terraform |
| Terraform state | Remote S3-backed state architecture |
| Application artifacts | Amazon ECR |
| CI validation and publication | Jenkins |
| Kubernetes desired state | GitOps repository |
| Kubernetes reconciliation | Argo CD |
| AWS workload identity | EKS Pod Identity + IAM |
| Public ingress | ALB + AWS Load Balancer Controller |
| TLS certificate | ACM |
| DNS | Route 53 / documented ownership boundary |

No single component is intentionally given authority over every layer.

---

## 46. Implemented Versus Future Controls

It is important to distinguish deployed controls from roadmap items.

### Implemented

- private EKS workload networking;
- private RDS;
- private Redis networking;
- Secrets Manager;
- Secrets Store CSI;
- EKS Pod Identity;
- private ECR;
- ALB ingress;
- ACM TLS;
- HTTP-to-HTTPS redirect;
- Argo CD;
- Jenkins/Argo CD separation;
- immutable image digests;
- hardened application containers;
- Terraform remote state;
- Terraform drift validation;
- GitOps reconciliation;
- controlled Argo CD bootstrap.

### Future Hardening

Potential later improvements include:

- MFA;
- enterprise SSO for Argo CD;
- comprehensive NetworkPolicy;
- Pod Security Admission enforcement;
- image signing;
- SBOM generation;
- provenance attestations;
- admission-time signature verification;
- formal WAF policy;
- centralized SIEM;
- automated secret rotation;
- expanded rate limiting.

Future controls must not be represented as currently deployed until they have
been implemented and validated.

---

## 47. Security Validation Summary

The development environment demonstrates security across multiple platform
layers:

```text
Source
  |
  v
Jenkins CI
  |
  +---- private immutable artifact ----> ECR
  |
  +---- desired-state update ----------> GitOps
                                            |
                                            v
                                         Argo CD
                                            |
                                            v
                                        Kubernetes
                                            |
                  +-------------------------+----------------------+
                  |                         |                      |
                  v                         v                      v
             Pod Identity            CSI Secrets             Private Data
                  |                         |                      |
                  v                         v                      v
                 IAM                 Secrets Manager          RDS / Redis
```

The platform demonstrates that security is not isolated to authentication or
networking. It is incorporated into:

- source control;
- CI;
- artifact management;
- GitOps;
- Kubernetes;
- AWS IAM;
- secret management;
- private networking;
- database access;
- container runtime configuration;
- infrastructure state;
- recovery;
- teardown.

This security model therefore represents the **as-built Platform Launchpad
development architecture**, while explicitly identifying controls that remain
future production-hardening work.