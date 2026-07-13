# Platform Launchpad — Requirements Traceability Matrix

## 1. Purpose

This matrix connects Platform Launchpad product requirements to architecture, API, UI, security, implementation, and testing deliverables.

It helps ensure that approved requirements are implemented and verified rather than existing only in documentation.

---

## 2. Traceability Matrix

| ID | Requirement | Design Reference | API or Interface | Planned Implementation | Verification |
|---|---|---|---|---|---|
| AUTH-001 | Users can register | Product requirements, security model | `POST /api/v1/auth/register` | FastAPI auth router and user service | Registration tests |
| AUTH-002 | Users can log in | API specification, security model | `POST /api/v1/auth/login` | Password verification and JWT service | Login tests |
| AUTH-003 | Passwords are never stored in plaintext | Security model | Internal control | Password-hashing service | Hashing tests and DB inspection |
| AUTH-004 | Disabled users cannot authenticate | Security model, database design | Login response `403` | Active-user validation | Disabled-user tests |
| AUTH-005 | Tokens expire | Security model, API specification | JWT access token | Token service | Expired-token tests |
| AUTHZ-001 | Users access only their own environments | Security model, ADR-0010 | Environment endpoints | Ownership dependency and service checks | Cross-user denial tests |
| AUTHZ-002 | Admin endpoints require admin role | Security model, UI wireframes | `/api/v1/admin/*` | Admin dependency | Role-denial tests |
| USER-001 | Users can view their profile | UI wireframes | `GET /api/v1/users/me` | User router | Current-user tests |
| ENV-001 | Users can create an environment | Product requirements, UI wireframes | `POST /api/v1/environments` | Environment service | Creation tests |
| ENV-002 | Users can list owned environments | API specification | `GET /api/v1/environments` | Environment repository | Filtering and ownership tests |
| ENV-003 | Users can view an environment | UI wireframes | `GET /api/v1/environments/{id}` | Environment router | Detail and authorization tests |
| ENV-004 | Users can request destruction | Database design, ADR-0008 | `POST /api/v1/environments/{id}/destroy` | Lifecycle service | Destruction tests |
| ENV-005 | Destroyed environments retain history | ADR-0008 | Environment detail response | Logical lifecycle state | Historical-record tests |
| ENV-006 | Duplicate active names are rejected | Database design | Environment creation conflict | Constraint and service validation | Conflict tests |
| LIFE-001 | Lifecycle transitions are validated | Database design | Environment lifecycle endpoints | State-transition service | Transition tests |
| LIFE-002 | Lifecycle work is asynchronous | Technical design | `202 Accepted` operations | Redis and worker | Queue integration tests |
| DEP-001 | Deployment requests preserve operation history | Database design | Deployment Request endpoints | Deployment Request model | History tests |
| AUD-001 | Security and lifecycle actions are audited | Security model | Admin audit endpoint | Audit service | Audit-event tests |
| AUD-002 | Audit logs exclude secrets | Security model | Audit-log responses | Sanitization controls | Redaction tests |
| HEALTH-001 | API exposes liveness | API specification | `GET /health/live` | Health router | Liveness test |
| HEALTH-002 | API exposes readiness | API specification | `GET /health/ready` | Dependency health checks | Database outage test |
| UI-001 | Users receive loading and error states | UI wireframes | Frontend pages | Next.js components | Frontend tests |
| UI-002 | Destruction requires confirmation | UI wireframes | Destroy modal | Confirmation component | Interaction tests |
| UI-003 | Navigation is role-aware | ADR-0009 | Application shell | Navigation guards | Role-navigation tests |
| SEC-001 | Secrets are excluded from Git | Security model | Repository control | `.gitignore` and scanning | Secret scan |
| SEC-002 | Backend validates all external input | Security model | All endpoints | Pydantic schemas | Validation tests |
| SEC-003 | Production traffic uses HTTPS | Security model, infrastructure design | ALB and ingress | ACM and ALB | TLS verification |
| DB-001 | PostgreSQL is the system of record | ADR-0003 | Database layer | SQLAlchemy and RDS | Integration tests |
| DB-002 | Schema changes use Alembic | Database design | Migration process | Alembic | Migration tests |
| CI-001 | Pull requests run automated checks | CI/CD design | Jenkins PR pipeline | Jenkinsfile | Pipeline execution |
| CI-002 | Images are scanned before publication | CI/CD design | Jenkins release pipeline | Trivy or equivalent | Pipeline gate |
| CI-003 | Runtime uses immutable image digests | ADR-0011 | GitOps manifests | ECR and Kustomize | Deployment inspection |
| CD-001 | Argo CD performs runtime reconciliation | ADR-0005 | GitOps repository | Argo CD Applications | Sync verification |
| CD-002 | Jenkins does not directly deploy workloads | ADR-0006 | Delivery architecture | GitOps update stage | Credential and pipeline review |
| INFRA-001 | AWS infrastructure is managed by Terraform | Infrastructure design | Terraform modules | Terraform | Plan and apply |
| INFRA-002 | Terraform uses remote state | Infrastructure design | S3 backend | Bootstrap module | Backend verification |
| INFRA-003 | Environments use separate state | ADR-0012 | Environment backends | Terraform directories | State-key inspection |
| INFRA-004 | RDS is not publicly accessible | Infrastructure design | Private database subnets | RDS module | AWS configuration review |
| INFRA-005 | Workloads use least-privilege IAM | Security and infrastructure designs | IRSA | IAM modules | Policy review |
| OBS-001 | API exposes Prometheus metrics | Observability design | `/metrics` | Metrics middleware | Metrics tests |
| OBS-002 | Logs are structured | Observability design | Application logs | Logging configuration | Log-format tests |
| OBS-003 | Request IDs correlate activity | API and observability designs | `X-Request-ID` | Request middleware | Correlation tests |
| OBS-004 | OpenTelemetry provides tracing | ADR-0013 | Trace propagation | OTel instrumentation | Trace verification |
| OBS-005 | Critical failures produce alerts | Observability design | Alertmanager | Prometheus rules | Alert tests |
| COST-001 | AWS resources can be torn down | Infrastructure design | Terraform destroy workflow | Jenkins or runbook | Teardown test |
| COST-002 | Cost thresholds are monitored | Infrastructure design | AWS Budgets | Budget module | AWS budget inspection |

---

## 3. Implementation Status Values

During implementation, each requirement may use one of these states:

```text
Not Started
In Progress
Implemented
Verified
Deferred
Blocked
```

The matrix should be updated during each implementation sprint.

---

## 4. Change Control

When a requirement changes:

1. Update the Product Requirements Document.
2. Update affected architecture documents.
3. Update the OpenAPI contract if applicable.
4. Update the UI wireframes if applicable.
5. Create or update an ADR for material decisions.
6. Update this traceability matrix.
7. Add or update automated tests.