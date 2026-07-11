# ADR-0010: Enforce Authorization in FastAPI

## Status

Accepted

## Context

Platform Launchpad uses a Next.js frontend and FastAPI backend.

The frontend displays different navigation and controls for regular users and administrators. However, browser-side controls can be modified or bypassed.

The platform must establish an authoritative security boundary for:

- Role enforcement
- Environment ownership
- User account status
- Lifecycle operations
- Administrative actions

## Decision

FastAPI will be the authoritative application authorization boundary.

Every protected backend operation will validate:

1. The request contains a valid access token.
2. The associated user exists.
3. The user account is active.
4. The user has the required role.
5. The user owns the requested resource when ownership is required.
6. The requested lifecycle transition is permitted.

Frontend role-aware navigation is treated only as a user-experience feature.

The backend must deny unauthorized requests even when a client calls the endpoint directly.

## Alternatives Considered

### Frontend-Only Authorization

Rejected because browser-side controls can be bypassed.

### API Gateway-Only Authorization

An API gateway may validate token presence, but it does not understand application ownership and lifecycle rules.

### Authorization Only in Database Queries

Query filtering is helpful but insufficient for all administrative and lifecycle operations.

### External Policy Engine for the MVP

A policy engine could centralize authorization, but it adds unnecessary complexity for the initial two-role model.

## Consequences

### Positive

- Authorization remains close to application domain logic.
- Direct API calls remain protected.
- Ownership rules are testable.
- Administrative controls are explicit.
- Frontend implementation does not define security.

### Negative

- Every protected route requires consistent dependencies and service checks.
- Authorization tests must cover both positive and negative cases.
- Future complex team and policy models may outgrow simple role checks.

## Review Conditions

Review this decision when:

- Team-based ownership is introduced.
- Additional roles are introduced.
- Policy-as-code becomes necessary.
- Multiple backend services require shared authorization rules.
- An external identity or policy provider is adopted.