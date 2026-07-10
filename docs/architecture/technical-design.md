# Platform Launchpad - Technical Design Document

## 1. Purpose

Platform Launchpad is a self-service internal developer platform demo application.

It allows authenticated users to request, view, and manage application environments through a web interface while platform automation handles environment lifecycle processing, deployment state, audit logging, and observability.

The application is intentionally designed to demonstrate both full-stack development and platform engineering capabilities.

---

## 2. Design Goals

The platform should:

- Provide a clear self-service experience for developers.
- Separate application responsibilities from platform automation.
- Support multiple users and role-based access control.
- Maintain a complete audit history of important actions.
- Support local development with Docker Compose.
- Support low-cost public hosting for portfolio demonstrations.
- Support a production-style deployment to AWS.
- Use CI/CD and GitOps for controlled application delivery.
- Provide health, metrics, logs, and tracing.
- Allow infrastructure to be destroyed and rebuilt through Terraform.

---

## 3. High-Level Architecture

The system consists of the following major components:

1. Next.js frontend
2. FastAPI backend API
3. PostgreSQL database
4. Background worker
5. Redis task queue
6. Jenkins CI pipeline
7. Container registry
8. GitOps repository
9. Argo CD
10. Kubernetes runtime
11. Observability stack
12. Terraform-managed AWS infrastructure

---

## 4. Application Components

### 4.1 Frontend

The frontend will be implemented using Next.js and TypeScript.

Responsibilities:

- User signup and login forms
- Dashboard rendering
- Environment request form
- Environment status display
- Admin views
- Audit-log presentation
- Calling the FastAPI backend
- Storing authentication state securely

The frontend will not communicate directly with PostgreSQL, Jenkins, Kubernetes, or AWS.

---

### 4.2 Backend API

The backend will be implemented using FastAPI.

Responsibilities:

- User registration
- User authentication
- JWT token generation and validation
- Role-based access control
- Environment CRUD operations
- Deployment request creation
- Audit logging
- Health and readiness endpoints
- Prometheus metrics endpoint
- Task submission to the worker queue

The backend is the primary authorization boundary for application operations.

---

### 4.3 PostgreSQL

PostgreSQL is the system of record.

It will store:

- Users
- Environments
- Deployment requests
- Audit logs
- Application metadata

PostgreSQL will run locally in Docker Compose.

For the AWS deployment, PostgreSQL will run in Amazon RDS.

---

### 4.4 Background Worker

The worker will be implemented in Python.

Responsibilities:

- Consume queued deployment requests
- Simulate or execute provisioning workflows
- Update environment lifecycle status
- Record audit events
- Handle retries and failures
- Publish task metrics

For the MVP, the worker will simulate provisioning by moving an environment through lifecycle states.

Later versions may integrate with Jenkins, Terraform, GitHub, or Kubernetes APIs.

---

### 4.5 Redis

Redis will provide:

- Background-task queue support
- Temporary task state
- Retry coordination
- Optional caching

Redis will be introduced when the background worker is implemented.

It is not required for the first database and authentication milestone.

---

## 5. Environment Lifecycle

An environment can have the following states:

- `pending`
- `provisioning`
- `active`
- `failed`
- `destroying`
- `destroyed`

### Creation Flow

1. A user submits an environment request.
2. The frontend sends the request to FastAPI.
3. FastAPI validates the request and user authorization.
4. FastAPI creates an environment record with status `pending`.
5. FastAPI creates a deployment-request record.
6. FastAPI submits a task to the worker queue.
7. The worker changes the status to `provisioning`.
8. The worker completes the simulated or real provisioning workflow.
9. The worker changes the status to `active` or `failed`.
10. Audit events are recorded throughout the workflow.

### Destruction Flow

1. A user requests environment deletion.
2. FastAPI verifies ownership or admin permissions.
3. The environment status changes to `destroying`.
4. A destruction task is queued.
5. The worker processes the task.
6. The environment status changes to `destroyed`.
7. The environment remains in the database for historical and audit purposes.

---

## 6. Authentication and Authorization

Authentication will initially use application-managed email and password credentials.

Passwords will be:

- Hashed before storage
- Never logged
- Never returned through API responses

The API will issue JWT access tokens.

Initial roles:

- `user`
- `admin`

### User Permissions

A regular user can:

- View their own profile
- Create environments
- View their own environments
- Request destruction of their own environments

### Admin Permissions

An admin can:

- View all users
- View all environments
- Update environment status
- View audit logs
- Manage failed requests

Authorization will be enforced in the FastAPI backend.

Frontend role checks are for display purposes only and are not considered a security boundary.

---

## 7. Local Development Architecture

Local development will use Docker Compose.

Services:

- PostgreSQL
- Redis
- FastAPI backend
- Python worker
- Next.js frontend

During early development, FastAPI and Next.js may run directly on the host while PostgreSQL runs in Docker.

This provides faster local development while retaining reproducible infrastructure.

---

## 8. Portfolio Hosting Architecture

The low-cost public demonstration environment may use:

- Vercel for the Next.js frontend
- Render or another lightweight platform for FastAPI
- Managed PostgreSQL with a free or low-cost tier
- A lightweight worker service

This environment exists so recruiters can access a stable live application without requiring an AWS environment to remain active.

---

## 9. AWS Platform Architecture

The production-style portfolio deployment will use:

- Amazon VPC
- Public and private subnets
- Amazon EKS
- Amazon ECR
- Amazon RDS for PostgreSQL
- AWS Secrets Manager
- Application Load Balancer
- Route 53
- ACM certificates
- IAM and IRSA
- CloudWatch
- S3 and DynamoDB for Terraform state

The AWS environment will be provisioned through Terraform and may be created only for demonstrations to control cost.

---

## 10. CI/CD Architecture

Jenkins will manage continuous integration.

The pipeline will:

1. Check out source code.
2. Install dependencies.
3. Run unit tests.
4. Run formatting and linting checks.
5. Run security scans.
6. Build Docker images.
7. Scan container images.
8. Push approved images to Amazon ECR.
9. Update the GitOps repository with the new image tag.
10. Allow Argo CD to reconcile the change.

Jenkins will not use direct `kubectl` access to deploy application workloads.

---

## 11. GitOps Architecture

Argo CD will manage Kubernetes application deployment.

The GitOps repository will contain:

- Base Kubernetes manifests
- Development overlays
- Staging overlays
- Production overlays
- Argo CD Application definitions

Deployment changes will occur through Git commits.

Rollback will be performed by reverting the GitOps commit or restoring a known-good image version.

---

## 12. Observability Architecture

The platform will expose:

- Application health endpoints
- Readiness endpoints
- Prometheus metrics
- Structured logs
- Distributed traces

Planned tools:

- Prometheus
- Grafana
- Loki
- Tempo or OpenTelemetry
- CloudWatch

Key application signals will include:

- Request rate
- Error rate
- Request latency
- Authentication failures
- Environment requests by status
- Worker queue depth
- Worker task duration
- Worker task failures
- Database connectivity
- Pod health
- Resource utilization

---

## 13. Security Boundaries

The main security boundaries are:

- Browser to frontend
- Frontend to backend API
- Backend to PostgreSQL
- Backend to Redis
- Worker to platform integrations
- Jenkins to ECR and GitHub
- Argo CD to Kubernetes
- Kubernetes workloads to AWS services

The backend API remains responsible for user authorization.

Infrastructure access will use least-privilege IAM roles.

Secrets will not be stored in Git.

---

## 14. Scalability

The architecture will support horizontal scaling of:

- Frontend replicas
- Backend replicas
- Worker replicas

The application services will be stateless.

Persistent state will reside in PostgreSQL and, where appropriate, Redis.

Kubernetes Horizontal Pod Autoscalers may later scale services based on CPU, memory, or custom metrics.

---

## 15. Failure Handling

The platform will handle failures through:

- Database transactions
- Worker retries
- Idempotent task processing
- Explicit failed states
- Structured error responses
- Readiness and liveness probes
- Alerting
- Audit logging

An environment request must not remain silently stuck without a status that can be investigated.

---

## 16. MVP Architecture Scope

The first implementation milestone includes:

- FastAPI backend
- PostgreSQL
- SQLAlchemy
- Alembic
- User model
- JWT authentication
- Role-based access control
- Environment model
- Deployment-request model
- Audit-log model
- Basic API tests

The following are deferred until later milestones:

- Redis
- Worker execution
- Next.js frontend
- Jenkins pipeline
- Kubernetes
- Terraform
- Argo CD
- Prometheus and Grafana
- AWS deployment