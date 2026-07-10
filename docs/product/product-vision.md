# Platform Launchpad — Product Vision

## 1. Vision Statement

Platform Launchpad is a production-style Internal Developer Platform demonstration that enables developers to request, manage, and observe application environments through a secure self-service portal.

The platform removes the need for application developers to interact directly with cloud consoles, Kubernetes clusters, Terraform state, or deployment credentials. Instead, it exposes governed workflows backed by automation, GitOps, infrastructure as code, audit logging, and observability.

Platform Launchpad is designed both as a functional application and as a portfolio case study demonstrating senior-level Platform Engineering practices.

---

## 2. Product Purpose

Engineering teams frequently need development, staging, demonstration, and preview environments.

Without a platform abstraction, developers may need to:

- Submit manual infrastructure tickets
- Wait for platform engineers to provision resources
- Run inconsistent deployment scripts
- Receive excessive cloud or Kubernetes permissions
- Diagnose failures across disconnected systems
- Depend on undocumented operational knowledge

Platform Launchpad provides a controlled interface for requesting and managing environments while platform automation handles the underlying workflow.

The product demonstrates how a Platform Engineering team can provide developer self-service without surrendering governance, security, traceability, or operational control.

---

## 3. Product Positioning

Platform Launchpad is not intended to replace enterprise products such as Backstage, Humanitec, Port, or commercial cloud management platforms.

It is a focused implementation of the core Internal Developer Platform concepts needed to demonstrate:

- Self-service workflows
- Platform APIs
- Role-based access control
- Asynchronous environment lifecycle operations
- Infrastructure automation
- GitOps-based delivery
- Observability
- Security boundaries
- Auditability
- Cost-conscious cloud operations

The system prioritizes clear architecture and defensible engineering decisions over excessive feature count.

---

## 4. Target Users

### 4.1 Application Developer

The application developer wants to request an environment without needing direct access to infrastructure tooling.

Primary needs:

- Create an environment quickly
- Choose an environment type
- Select an application version
- Track provisioning status
- Access the deployed application
- Request environment destruction
- Understand failures without contacting multiple teams

### 4.2 Platform Administrator

The platform administrator governs environment lifecycle operations.

Primary needs:

- View all users and environments
- Review failed provisioning requests
- Inspect audit history
- Retry or manage failed operations
- Enforce supported environment types
- Maintain platform reliability
- Control access and operational risk

### 4.3 Hiring Manager or Interviewer

The interviewer evaluates the project as an engineering case study.

Primary needs:

- Understand the architecture quickly
- See clear engineering tradeoffs
- Review production-style documentation
- Inspect implementation quality
- Observe CI/CD, GitOps, IaC, security, and monitoring practices
- See how the system handles failure, rollback, scaling, and cost

This user persona is specific to the portfolio purpose of the project.

---

## 5. Problem Statement

Developers need fast access to application environments, but direct access to infrastructure creates security, consistency, and governance risks.

Traditional ticket-based provisioning introduces delays and depends heavily on manual platform-team intervention.

Platform Launchpad addresses this problem by providing a self-service workflow in which:

1. A developer requests an environment.
2. The platform validates the request.
3. The system records the request and ownership.
4. A background workflow processes the lifecycle operation.
5. The developer sees the current status.
6. Every meaningful action is recorded.
7. Runtime deployment remains controlled through GitOps.

---

## 6. Product Principles

### 6.1 Self-Service with Guardrails

Developers should be able to perform approved platform operations without receiving direct administrative access.

### 6.2 Git as the Runtime Source of Truth

Runtime deployment state should be represented in Git and reconciled by Argo CD.

### 6.3 CI Does Not Equal Deployment Access

Jenkins should validate, build, scan, publish, and update desired state. It should not require direct `kubectl` access to application clusters.

### 6.4 Infrastructure Must Be Reproducible

AWS infrastructure should be created, modified, and destroyed through Terraform rather than undocumented console actions.

### 6.5 Security Is Enforced Server-Side

Frontend permissions improve usability, but the FastAPI backend remains the application authorization boundary.

### 6.6 Long-Running Work Is Asynchronous

Provisioning and destruction should not block HTTP requests. They should be processed through background workflows.

### 6.7 Operational History Is Preserved

Environment and deployment history should remain available after resources are destroyed.

### 6.8 Observability Is Part of the Product

Health, metrics, logs, traces, and meaningful audit events are required platform capabilities rather than optional additions.

### 6.9 Cost Is an Architectural Constraint

The public portfolio demonstration must remain inexpensive, while the complete AWS architecture may be provisioned only when required.

### 6.10 Documentation Evolves with the System

Architecture documents, ADRs, API contracts, and operational guidance should be updated alongside implementation changes.

---

## 7. Product Goals

### Goal 1: Provide a Developer Self-Service Experience

Users can register, authenticate, request environments, observe lifecycle state, and request destruction through a web interface.

### Goal 2: Demonstrate Platform Governance

The platform validates supported operations and ensures users can access only resources they own unless they are administrators.

### Goal 3: Demonstrate End-to-End Delivery

The project connects application code, Jenkins, container images, Amazon ECR, GitOps configuration, Argo CD, and Kubernetes.

### Goal 4: Demonstrate Infrastructure Automation

Terraform provisions the AWS networking, security, compute, database, and supporting platform resources.

### Goal 5: Demonstrate Operational Readiness

The system exposes health signals, structured logs, metrics, traces, dashboards, alerts, retries, and failure states.

### Goal 6: Produce an Interview-Ready Case Study

The repository should clearly explain the problem, architecture, decisions, implementation, security, operations, cost controls, and lessons learned.

---

## 8. Non-Goals

The initial product will not attempt to provide:

- Full enterprise service catalog functionality
- Enterprise SSO in the MVP
- Multi-cloud infrastructure provisioning
- Production-grade financial chargeback
- Complex policy-as-code enforcement
- Full Kubernetes namespace tenancy
- Arbitrary Terraform execution submitted by users
- Direct access to the AWS console
- Direct access to Kubernetes credentials
- Full Backstage plugin compatibility
- A marketplace of unlimited environment templates
- Production customer workloads

These areas may be discussed as future extensions but are not required for the initial release.

---

## 9. MVP Capabilities

### Authentication

- User registration
- User login
- Secure password hashing
- JWT access tokens
- Active and disabled user state

### Authorization

- `user` role
- `admin` role
- Environment ownership enforcement
- Administrator-only operations

### Environment Management

- Create an environment request
- Select environment type
- Select application version
- View owned environments
- View environment details
- Request environment destruction
- Preserve destroyed environment history

### Lifecycle Tracking

- `pending`
- `provisioning`
- `active`
- `failed`
- `destroying`
- `destroyed`

### Deployment Requests

- Record provision operations
- Record destroy operations
- Track queued, processing, successful, failed, and cancelled states
- Preserve retry and failure information

### Auditability

- Record registration
- Record successful and failed login activity
- Record environment creation
- Record lifecycle changes
- Record administrative actions
- Exclude passwords, tokens, and secrets

### Local Execution

- FastAPI backend
- Next.js frontend
- PostgreSQL
- Redis
- Python worker
- Docker Compose

---

## 10. Future Capabilities

Future releases may include:

- Environment templates
- Team ownership
- Approval workflows
- Resource quotas
- Cost estimates
- Cost reporting
- Preview environments
- Scheduled expiration
- Notifications
- Webhooks
- API tokens
- Service accounts
- Policy-as-code integration
- Automated rollback
- Canary deployment
- Multi-cluster support
- Multi-region deployment
- Enterprise identity federation
- Platform scorecards
- Service catalog integration

These features must not block delivery of the MVP.

---

## 11. User Experience Vision

A developer should be able to complete the main workflow without understanding Terraform, Kubernetes, Jenkins, Argo CD, or AWS internals.

The intended experience is:

1. Sign in.
2. Open the dashboard.
3. Select **Create Environment**.
4. Enter a name.
5. Choose `development`, `staging`, or `demo`.
6. Choose an application version.
7. Submit the request.
8. Observe the status move from `pending` to `provisioning`.
9. Open the application when the status becomes `active`.
10. Request destruction when the environment is no longer needed.
11. Retain access to historical lifecycle details.

Errors should be visible, actionable, and correlated with a deployment request.

---

## 12. Platform Administrator Experience

An administrator should be able to:

1. Sign in using an administrator account.
2. View system-wide environment status.
3. Identify pending, active, failed, and destroying environments.
4. Review the user who initiated an operation.
5. Inspect a deployment-request history.
6. Review sanitized failure information.
7. Review audit events.
8. Disable a user when necessary.
9. Retry or resolve supported failed operations.
10. Confirm that system activity is visible through dashboards and alerts.

---

## 13. Portfolio Experience

A reviewer should be able to understand the project through the repository without deploying it.

The repository should expose:

- Product vision
- Product requirements
- Technical design
- System architecture
- Architecture Decision Records
- Database design
- API specification
- UI wireframes
- Security model
- CI/CD design
- Infrastructure design
- GitOps design
- Observability design
- Runbooks
- Screenshots
- Architecture diagrams
- Demonstration video
- Lessons learned
- Interview talking points

The live application should complement the repository rather than replace its documentation.

---

## 14. Success Metrics

### Product Success

- A user can register and authenticate.
- A user can create an environment request.
- A user can access only their own environments.
- An administrator can access system-wide views.
- Lifecycle state is accurately persisted.
- Destruction preserves historical data.
- Failed operations remain discoverable.

### Engineering Success

- Database changes are managed by Alembic.
- API behavior matches the documented contract.
- Unit and integration tests protect critical workflows.
- Container images are reproducible.
- CI performs validation, testing, and scanning.
- Runtime deployment follows GitOps.
- Terraform can recreate the AWS environment.
- Secrets are excluded from Git.
- Health and telemetry are available.
- Rollback procedures are documented.

### Portfolio Success

- The architecture can be understood in under ten minutes.
- The project can support a ten-to-fifteen-minute demonstration.
- The project produces credible Senior Platform Engineer interview stories.
- A recruiter can access a low-cost live demonstration.
- AWS resources can be destroyed when not in use.

---

## 15. Constraints

### Cost Constraint

The public demonstration should use free or limited-cost services where practical.

The AWS environment should support on-demand creation and teardown.

### Resource Constraint

The local environment must remain usable on a developer workstation with limited CPU and memory.

Heavy Kubernetes and observability workloads do not need to run locally at all times.

### Security Constraint

The project must not commit:

- Passwords
- JWT secrets
- AWS credentials
- Database credentials
- Private keys
- Tokens
- Sensitive production data

### Scope Constraint

The MVP must remain small enough to complete while still demonstrating a full engineering lifecycle.

---

## 16. Key Risks

### Risk: Excessive Scope

The project includes application, platform, security, delivery, infrastructure, and observability work.

Mitigation:

- Deliver capabilities incrementally.
- Defer non-MVP features.
- Use explicit sprint acceptance criteria.
- Avoid adding services without a defined purpose.

### Risk: Cloud Cost

EKS, RDS, load balancers, NAT gateways, and observability services can create ongoing charges.

Mitigation:

- Maintain a lightweight hosted demonstration.
- Provision AWS only when required.
- Provide teardown automation.
- Apply budgets and cost alerts.
- Document estimated costs.

### Risk: Security Complexity

Application-managed authentication introduces security responsibilities.

Mitigation:

- Use mature password-hashing libraries.
- Use short-lived access tokens.
- Enforce server-side authorization.
- Add rate limiting and secure configuration in later hardening phases.
- Treat the MVP implementation as a demonstration rather than an identity product.

### Risk: Provisioning Workflow Complexity

Real infrastructure provisioning can be slow and failure-prone.

Mitigation:

- Begin with simulated workflows.
- Introduce idempotency.
- Persist operation state.
- Add retries.
- Keep Terraform execution governed.
- Expose actionable status information.

### Risk: Portfolio Availability

An AWS environment may be unavailable after teardown.

Mitigation:

- Host a lightweight persistent demonstration separately.
- Provide screenshots and a Loom walkthrough.
- Keep architecture documentation complete.

---

## 17. Delivery Strategy

The product will be delivered incrementally.

### Sprint 0 — Product and Architecture Design

Define:

- Product vision
- Requirements
- Architecture
- ADRs
- Database design
- API contract
- UI wireframes
- Security
- CI/CD
- Infrastructure
- Observability

### Sprint 1 — Backend Foundation

Implement:

- Configuration
- SQLAlchemy
- Alembic
- Database models
- Authentication
- RBAC
- Health endpoints
- Initial tests

### Sprint 2 — Environment Management

Implement:

- Environment APIs
- Deployment-request APIs
- Audit events
- Lifecycle validation
- Service-layer rules

### Sprint 3 — Worker and Queue

Implement:

- Redis
- Background worker
- Simulated provisioning
- Retry behavior
- Failure handling

### Sprint 4 — Frontend

Implement:

- Authentication pages
- User dashboard
- Environment request flow
- Environment detail page
- Administrator views

### Sprint 5 — Containerization and Local Platform

Implement:

- Service Dockerfiles
- Docker Compose
- Health checks
- Local integration testing
- Developer documentation

### Sprint 6 — CI/CD and Security

Implement:

- Jenkins pipeline
- Tests
- Linting
- SonarQube
- Dependency scanning
- Container scanning
- ECR publishing

### Sprint 7 — Infrastructure

Implement:

- Terraform modules
- AWS networking
- IAM
- EKS
- RDS
- ECR
- Secrets
- DNS and certificates

### Sprint 8 — GitOps

Implement:

- Kubernetes manifests
- Kustomize overlays
- Argo CD applications
- Environment promotion
- Rollback

### Sprint 9 — Observability and Reliability

Implement:

- Metrics
- Logs
- Traces
- Dashboards
- Alerts
- Autoscaling
- Runbooks

### Sprint 10 — Portfolio Release

Produce:

- Final diagrams
- Case study
- GitHub Pages
- Loom walkthrough
- Resume bullets
- Interview stories

---

## 18. Definition of Product Completion

Platform Launchpad reaches its first complete portfolio release when:

- The documented MVP works end to end.
- Core workflows are protected by automated tests.
- The application runs through Docker Compose.
- A low-cost public demonstration is available.
- The AWS architecture is reproducible through Terraform.
- Application delivery uses Jenkins and GitOps.
- Observability covers application and worker workflows.
- Security boundaries and assumptions are documented.
- Teardown and rebuild procedures are tested.
- Architecture diagrams match the implemented system.
- The repository contains a complete case study.