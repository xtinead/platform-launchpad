# Platform Launchpad — API Specification

## 1. Purpose

This document defines the REST API contract for Platform Launchpad.

The API supports:

- User registration and authentication
- Current-user profile access
- Environment creation and lifecycle management
- Deployment-request tracking
- Administrative user and environment management
- Audit-log review
- Health and readiness checks

The API is implemented with FastAPI and follows an OpenAPI-first design approach.

The machine-readable contract is located at:

```text
docs/api/openapi.yaml
```

---

## 2. API Design Principles

The API follows these principles:

- Use versioned REST endpoints.
- Use JSON for request and response bodies.
- Use UUIDs for public resource identifiers.
- Enforce authentication and authorization server-side.
- Return consistent error responses.
- Preserve historical environment and deployment records.
- Use asynchronous lifecycle operations for provisioning and destruction.
- Avoid returning passwords, password hashes, tokens, secrets, or internal credentials.
- Use UTC timestamps serialized as ISO 8601.
- Use appropriate HTTP status codes.
- Document every endpoint before implementation.

---

## 3. Base Paths

Application API:

```text
/api/v1
```

Health endpoints:

```text
/health
```

Example local base URL:

```text
http://localhost:8000
```

Example API endpoint:

```text
http://localhost:8000/api/v1/environments
```

---

## 4. Content Types

Requests containing a JSON body use:

```http
Content-Type: application/json
```

Responses use:

```http
Content-Type: application/json
```

The login endpoint will initially use JSON credentials rather than form-encoded OAuth2 credentials.

---

## 5. Authentication

Platform Launchpad uses bearer JWT access tokens.

Authenticated requests include:

```http
Authorization: Bearer <access-token>
```

The JWT includes:

- User identifier
- User role
- Issued-at timestamp
- Expiration timestamp
- Token type

Example claims:

```json
{
  "sub": "7ce8938a-4055-439b-b941-794682a72463",
  "role": "user",
  "type": "access",
  "iat": 1783700000,
  "exp": 1783703600
}
```

The MVP uses access tokens only.

Refresh tokens, token revocation lists, and enterprise identity federation are deferred to later releases.

When an access token expires, the user must authenticate again.

---

## 6. Roles

Supported application roles:

- `user`
- `admin`

### User Permissions

A regular user may:

- Read their own profile
- Create environments
- List their own environments
- Read their own environment details
- Request destruction of their own environments
- Read deployment requests associated with their environments

### Administrator Permissions

An administrator may:

- Perform all regular-user operations
- List all users
- Enable or disable users
- List all environments
- Read all environments
- Review all deployment requests
- Retry supported failed requests
- Review audit logs
- Perform controlled environment-status overrides

Frontend role checks do not replace backend authorization.

---

## 7. Resource Naming

Resource names use plural nouns.

Examples:

```text
/users
/environments
/deployment-requests
/audit-logs
```

Path parameters use UUID identifiers:

```text
/environments/{environment_id}
```

Actions that do not map cleanly to CRUD use explicit action endpoints:

```text
/environments/{environment_id}/destroy
/deployment-requests/{request_id}/retry
```

---

## 8. Timestamp Format

All timestamps use ISO 8601 UTC format.

Example:

```text
2026-07-10T14:30:00Z
```

The frontend is responsible for converting timestamps to the user's display timezone.

---

## 9. Pagination

Collection endpoints use page-based pagination for the MVP.

Query parameters:

| Parameter | Type | Default | Limits | Description |
|---|---|---:|---|---|
| `page` | Integer | `1` | Minimum `1` | Requested page |
| `page_size` | Integer | `20` | Minimum `1`, maximum `100` | Results per page |

Example:

```http
GET /api/v1/environments?page=2&page_size=20
```

Paginated responses use:

```json
{
  "items": [],
  "pagination": {
    "page": 2,
    "page_size": 20,
    "total_items": 58,
    "total_pages": 3
  }
}
```

A future release may replace page-based pagination with cursor-based pagination for large datasets.

---

## 10. Filtering

Collection endpoints may support filters.

Environment filters:

- `status`
- `environment_type`
- `owner_id` for administrators
- `name`
- `created_from`
- `created_to`

Deployment-request filters:

- `status`
- `operation`
- `environment_id`
- `requested_by_id` for administrators

Audit-log filters:

- `action`
- `result`
- `resource_type`
- `user_id`
- `environment_id`
- `created_from`
- `created_to`

Invalid filter values return `422 Unprocessable Entity`.

---

## 11. Sorting

Collection endpoints may support:

```text
sort_by
sort_order
```

Supported values depend on the resource.

Common `sort_order` values:

- `asc`
- `desc`

Default ordering:

- Environments: `created_at desc`
- Deployment requests: `requested_at desc`
- Audit logs: `created_at desc`
- Users: `created_at desc`

---

## 12. Standard Error Response

All handled API errors use a consistent envelope.

```json
{
  "error": {
    "code": "environment_not_found",
    "message": "The requested environment was not found.",
    "details": {},
    "request_id": "req_8c071f3102a24fbb"
  }
}
```

Fields:

| Field | Description |
|---|---|
| `code` | Stable machine-readable error identifier |
| `message` | Safe human-readable explanation |
| `details` | Optional structured error context |
| `request_id` | Correlation identifier for troubleshooting |

Sensitive internal exceptions must not be exposed to clients.

---

## 13. Common Error Codes

| Code | HTTP Status | Meaning |
|---|---:|---|
| `validation_error` | 422 | Request validation failed |
| `authentication_required` | 401 | Bearer token is missing |
| `invalid_credentials` | 401 | Login credentials are incorrect |
| `invalid_token` | 401 | JWT is malformed or invalid |
| `token_expired` | 401 | JWT has expired |
| `account_disabled` | 403 | User account is disabled |
| `permission_denied` | 403 | User lacks permission |
| `resource_not_found` | 404 | Generic resource was not found |
| `user_not_found` | 404 | User was not found |
| `environment_not_found` | 404 | Environment was not found |
| `deployment_request_not_found` | 404 | Deployment request was not found |
| `email_already_registered` | 409 | Email is already in use |
| `environment_name_conflict` | 409 | Active environment name already exists |
| `invalid_state_transition` | 409 | Lifecycle transition is not allowed |
| `operation_already_in_progress` | 409 | Conflicting lifecycle operation exists |
| `internal_server_error` | 500 | Unexpected server failure |
| `service_unavailable` | 503 | Required dependency is unavailable |

---

# 14. Health Endpoints

## 14.1 Liveness

```http
GET /health/live
```

Purpose:

Confirms that the API process is running.

Authentication:

Not required.

Successful response:

```http
200 OK
```

```json
{
  "status": "ok",
  "service": "platform-launchpad-api"
}
```

The liveness endpoint must not perform expensive dependency checks.

---

## 14.2 Readiness

```http
GET /health/ready
```

Purpose:

Confirms that the API can serve traffic and connect to required dependencies.

Initial dependency:

- PostgreSQL

Later dependencies may include:

- Redis

Successful response:

```http
200 OK
```

```json
{
  "status": "ready",
  "checks": {
    "database": "ok"
  }
}
```

Unavailable dependency response:

```http
503 Service Unavailable
```

```json
{
  "error": {
    "code": "service_unavailable",
    "message": "The service is not ready to receive traffic.",
    "details": {
      "database": "unavailable"
    },
    "request_id": "req_bfbc295ceec64104"
  }
}
```

---

# 15. Authentication Endpoints

## 15.1 Register User

```http
POST /api/v1/auth/register
```

Authentication:

Not required.

Request:

```json
{
  "email": "developer@example.com",
  "password": "ExamplePassword123!",
  "full_name": "Example Developer"
}
```

Validation:

- Email must be valid.
- Email is normalized to lowercase.
- Password must satisfy the password policy.
- Full name must be between 2 and 150 characters.
- Public registration always creates the `user` role.
- Clients cannot assign themselves the `admin` role.

Successful response:

```http
201 Created
```

```json
{
  "id": "7ce8938a-4055-439b-b941-794682a72463",
  "email": "developer@example.com",
  "full_name": "Example Developer",
  "role": "user",
  "is_active": true,
  "created_at": "2026-07-10T14:30:00Z",
  "updated_at": "2026-07-10T14:30:00Z",
  "last_login_at": null
}
```

Possible errors:

- `422 validation_error`
- `409 email_already_registered`

Audit action:

```text
user.registered
```

---

## 15.2 Login

```http
POST /api/v1/auth/login
```

Authentication:

Not required.

Request:

```json
{
  "email": "developer@example.com",
  "password": "ExamplePassword123!"
}
```

Successful response:

```http
200 OK
```

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "7ce8938a-4055-439b-b941-794682a72463",
    "email": "developer@example.com",
    "full_name": "Example Developer",
    "role": "user",
    "is_active": true
  }
}
```

Possible errors:

- `401 invalid_credentials`
- `403 account_disabled`
- `422 validation_error`

The API should use a generic invalid-credentials message to avoid revealing whether an email exists.

Audit actions:

```text
user.login_succeeded
user.login_failed
```

---

# 16. Current User Endpoints

## 16.1 Get Current User

```http
GET /api/v1/users/me
```

Authentication:

Required.

Successful response:

```http
200 OK
```

```json
{
  "id": "7ce8938a-4055-439b-b941-794682a72463",
  "email": "developer@example.com",
  "full_name": "Example Developer",
  "role": "user",
  "is_active": true,
  "created_at": "2026-07-10T14:30:00Z",
  "updated_at": "2026-07-10T14:30:00Z",
  "last_login_at": "2026-07-10T15:00:00Z"
}
```

Possible errors:

- `401 authentication_required`
- `401 invalid_token`
- `401 token_expired`
- `403 account_disabled`

---

# 17. Environment Endpoints

## 17.1 Create Environment

```http
POST /api/v1/environments
```

Authentication:

Required.

Request:

```json
{
  "name": "payments-demo",
  "environment_type": "demo",
  "application_version": "1.4.2",
  "description": "Demo environment for the payments application"
}
```

Validation:

- Name must be between 3 and 100 characters.
- Name must use supported characters.
- Environment type must be supported.
- Application version is required.
- The owner is derived from the authenticated user.
- A user cannot create a second non-destroyed environment with the same name.

Successful response:

```http
202 Accepted
```

```json
{
  "environment": {
    "id": "397f1cc1-2750-4182-94a8-c7c53de71df4",
    "owner_id": "7ce8938a-4055-439b-b941-794682a72463",
    "name": "payments-demo",
    "environment_type": "demo",
    "application_version": "1.4.2",
    "description": "Demo environment for the payments application",
    "status": "pending",
    "external_url": null,
    "metadata": {},
    "created_at": "2026-07-10T15:15:00Z",
    "updated_at": "2026-07-10T15:15:00Z",
    "destroyed_at": null
  },
  "deployment_request": {
    "id": "4df37e1a-e920-41ca-9548-b170d0043dcf",
    "environment_id": "397f1cc1-2750-4182-94a8-c7c53de71df4",
    "requested_by_id": "7ce8938a-4055-439b-b941-794682a72463",
    "operation": "provision",
    "status": "queued",
    "attempt_count": 0,
    "requested_at": "2026-07-10T15:15:00Z",
    "started_at": null,
    "completed_at": null,
    "updated_at": "2026-07-10T15:15:00Z"
  }
}
```

The response is `202 Accepted` because provisioning is asynchronous.

Possible errors:

- `401 authentication_required`
- `403 account_disabled`
- `409 environment_name_conflict`
- `422 validation_error`

Audit action:

```text
environment.created
```

---

## 17.2 List Environments

```http
GET /api/v1/environments
```

Authentication:

Required.

Regular users receive only environments they own.

Administrators may use the administrative endpoint to retrieve system-wide results.

Supported query parameters:

- `page`
- `page_size`
- `status`
- `environment_type`
- `name`
- `sort_by`
- `sort_order`

Successful response:

```http
200 OK
```

```json
{
  "items": [
    {
      "id": "397f1cc1-2750-4182-94a8-c7c53de71df4",
      "owner_id": "7ce8938a-4055-439b-b941-794682a72463",
      "name": "payments-demo",
      "environment_type": "demo",
      "application_version": "1.4.2",
      "description": "Demo environment for the payments application",
      "status": "active",
      "external_url": "https://payments-demo.example.com",
      "metadata": {},
      "created_at": "2026-07-10T15:15:00Z",
      "updated_at": "2026-07-10T15:20:00Z",
      "destroyed_at": null
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 1,
    "total_pages": 1
  }
}
```

---

## 17.3 Get Environment

```http
GET /api/v1/environments/{environment_id}
```

Authentication:

Required.

Authorization:

- The requester must own the environment, or
- The requester must be an administrator.

Successful response:

```http
200 OK
```

Response body:

An environment object.

Possible errors:

- `403 permission_denied`
- `404 environment_not_found`

The API may return `404` instead of `403` for unauthorized resource access to reduce resource enumeration.

---

## 17.4 Request Environment Destruction

```http
POST /api/v1/environments/{environment_id}/destroy
```

Authentication:

Required.

Authorization:

- Environment owner, or
- Administrator

Request body:

No body is required for the MVP.

Successful response:

```http
202 Accepted
```

```json
{
  "environment": {
    "id": "397f1cc1-2750-4182-94a8-c7c53de71df4",
    "status": "destroying",
    "updated_at": "2026-07-10T17:00:00Z"
  },
  "deployment_request": {
    "id": "98e09eca-d6e6-4e69-a1ed-4a41d0124e62",
    "environment_id": "397f1cc1-2750-4182-94a8-c7c53de71df4",
    "operation": "destroy",
    "status": "queued",
    "requested_at": "2026-07-10T17:00:00Z"
  }
}
```

Possible errors:

- `404 environment_not_found`
- `409 invalid_state_transition`
- `409 operation_already_in_progress`

Audit action:

```text
environment.destroy_requested
```

---

## 17.5 List Environment Deployment Requests

```http
GET /api/v1/environments/{environment_id}/deployment-requests
```

Authentication:

Required.

Authorization:

- Environment owner, or
- Administrator

Supported query parameters:

- `page`
- `page_size`
- `status`
- `operation`

Successful response:

```http
200 OK
```

```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 0,
    "total_pages": 0
  }
}
```

---

# 18. Deployment Request Endpoints

## 18.1 Get Deployment Request

```http
GET /api/v1/deployment-requests/{request_id}
```

Authentication:

Required.

Authorization:

- Requester owns the associated environment, or
- Requester is an administrator

Successful response:

```http
200 OK
```

```json
{
  "id": "4df37e1a-e920-41ca-9548-b170d0043dcf",
  "environment_id": "397f1cc1-2750-4182-94a8-c7c53de71df4",
  "requested_by_id": "7ce8938a-4055-439b-b941-794682a72463",
  "operation": "provision",
  "status": "succeeded",
  "attempt_count": 1,
  "error_message": null,
  "request_payload": {
    "requested_version": "1.4.2"
  },
  "requested_at": "2026-07-10T15:15:00Z",
  "started_at": "2026-07-10T15:15:05Z",
  "completed_at": "2026-07-10T15:20:00Z",
  "updated_at": "2026-07-10T15:20:00Z"
}
```

---

# 19. Administrative Endpoints

All administrative endpoints require the `admin` role.

## 19.1 List Users

```http
GET /api/v1/admin/users
```

Supported filters:

- `role`
- `is_active`
- `email`
- `page`
- `page_size`

Successful response:

```http
200 OK
```

```json
{
  "items": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 0,
    "total_pages": 0
  }
}
```

---

## 19.2 Update User Status

```http
PATCH /api/v1/admin/users/{user_id}
```

Request:

```json
{
  "is_active": false
}
```

Successful response:

```http
200 OK
```

Response body:

Updated user object.

Possible errors:

- `404 user_not_found`
- `422 validation_error`

Audit actions:

```text
admin.user_disabled
admin.user_enabled
```

The MVP does not permit changing a user's role through this endpoint.

Role management may be added later with stronger safeguards.

---

## 19.3 List All Environments

```http
GET /api/v1/admin/environments
```

Supported filters:

- `owner_id`
- `status`
- `environment_type`
- `name`
- `page`
- `page_size`
- `sort_by`
- `sort_order`

Successful response:

```http
200 OK
```

Returns the standard paginated environment response.

---

## 19.4 Override Environment Status

```http
PATCH /api/v1/admin/environments/{environment_id}/status
```

This endpoint exists for controlled administrative recovery.

Request:

```json
{
  "status": "failed",
  "reason": "Provisioning worker timed out and manual investigation is required."
}
```

Successful response:

```http
200 OK
```

Possible errors:

- `404 environment_not_found`
- `409 invalid_state_transition`
- `422 validation_error`

Every override must produce an audit event.

Audit action:

```text
environment.status_changed
```

The endpoint must not bypass all state-transition rules without an explicit documented reason.

---

## 19.5 Retry Deployment Request

```http
POST /api/v1/admin/deployment-requests/{request_id}/retry
```

Only failed deployment requests may be retried.

Successful response:

```http
202 Accepted
```

```json
{
  "original_request_id": "4df37e1a-e920-41ca-9548-b170d0043dcf",
  "retry_request": {
    "id": "0c435303-cb41-4e3a-829c-c3c53cc63a2f",
    "operation": "retry",
    "status": "queued",
    "attempt_count": 0
  }
}
```

Possible errors:

- `404 deployment_request_not_found`
- `409 invalid_state_transition`
- `409 operation_already_in_progress`

---

## 19.6 List Audit Logs

```http
GET /api/v1/admin/audit-logs
```

Supported filters:

- `user_id`
- `environment_id`
- `deployment_request_id`
- `action`
- `resource_type`
- `result`
- `created_from`
- `created_to`
- `page`
- `page_size`

Successful response:

```http
200 OK
```

```json
{
  "items": [
    {
      "id": "2bc7bc59-c9d9-4e33-81ea-ae682731578b",
      "user_id": "7ce8938a-4055-439b-b941-794682a72463",
      "environment_id": "397f1cc1-2750-4182-94a8-c7c53de71df4",
      "deployment_request_id": null,
      "action": "environment.created",
      "resource_type": "environment",
      "resource_id": "397f1cc1-2750-4182-94a8-c7c53de71df4",
      "result": "success",
      "message": "Environment request created.",
      "details": {},
      "source_ip": "192.0.2.10",
      "created_at": "2026-07-10T15:15:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 1,
    "total_pages": 1
  }
}
```

Audit logs are read-only through the API.

---

# 20. HTTP Status Code Standards

| Status | Usage |
|---:|---|
| `200 OK` | Successful read or update |
| `201 Created` | Synchronous resource creation |
| `202 Accepted` | Asynchronous lifecycle operation accepted |
| `204 No Content` | Successful operation without a response body |
| `400 Bad Request` | Malformed request outside schema validation |
| `401 Unauthorized` | Authentication missing or invalid |
| `403 Forbidden` | Authenticated user lacks permission |
| `404 Not Found` | Resource does not exist or is intentionally concealed |
| `409 Conflict` | State or uniqueness conflict |
| `422 Unprocessable Entity` | Request schema or parameter validation failed |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Unexpected server failure |
| `503 Service Unavailable` | Required dependency is unavailable |

---

# 21. Password Policy

The initial password policy requires:

- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Maximum 128 characters

Passwords must never be:

- Logged
- Returned
- Stored as plaintext
- Stored in audit details

A future release may use breached-password screening and stronger identity controls.

---

# 22. Rate Limiting

Rate limiting is deferred from the first backend milestone but remains a security requirement.

Priority endpoints for rate limiting:

- Registration
- Login
- Environment creation
- Environment destruction
- Administrative retries

Expected login behavior:

```http
429 Too Many Requests
```

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Too many requests. Please try again later.",
    "details": {},
    "request_id": "req_e1fca93caea84bb3"
  }
}
```

---

# 23. Request Correlation

Every request should have a correlation identifier.

Accepted request header:

```http
X-Request-ID: client-generated-id
```

If absent, the API generates one.

Response header:

```http
X-Request-ID: req_8c071f3102a24fbb
```

The identifier should be included in:

- Structured logs
- Error responses
- Worker tasks
- Audit context where useful
- Distributed traces

---

# 24. API Versioning

The MVP uses path-based versioning:

```text
/api/v1
```

Breaking changes require a new version.

Examples of breaking changes:

- Removing a field
- Renaming a field
- Changing a field's type
- Changing authorization semantics
- Changing lifecycle behavior incompatibly

Additive optional fields may be introduced without creating a new API version.

---

# 25. Idempotency

Provisioning and destruction operations should eventually support idempotency.

Planned header:

```http
Idempotency-Key: <client-generated-value>
```

The first implementation may rely on transaction checks and lifecycle conflict detection.

Explicit idempotency-key persistence may be introduced with the worker milestone.

---

# 26. OpenAPI Requirements

The machine-readable OpenAPI contract must define:

- All documented paths
- Request and response schemas
- Bearer authentication
- UUID formats
- Date-time formats
- Enumerations
- Standard error responses
- Pagination schemas
- Administrative authorization descriptions
- Example payloads

FastAPI implementation should be compared with the approved contract during Sprint 1.

---

# 27. API Acceptance Criteria

The API design is complete when:

- Authentication endpoints are documented.
- User endpoints are documented.
- Environment endpoints are documented.
- Deployment-request endpoints are documented.
- Administrative endpoints are documented.
- Health endpoints are documented.
- Authorization rules are defined.
- Lifecycle conflicts are defined.
- Request and response examples are included.
- Standard error behavior is defined.
- Pagination and filtering are defined.
- The OpenAPI document validates successfully.
- The implementation can be mapped directly from the approved contract.