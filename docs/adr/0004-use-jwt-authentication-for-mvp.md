# ADR-0004: Use Application-Managed JWT Authentication for the MVP

## Status

Accepted

## Context

Platform Launchpad requires basic multi-user support with:

- Registration
- Login
- Authenticated API requests
- User and administrator roles
- Environment ownership
- A low-cost implementation
- Minimal dependence on third-party identity services

The first release is a portfolio demonstration rather than an enterprise identity platform.

The authentication model should be quick to implement while still demonstrating password hashing, token validation, server-side authorization, and secure configuration.

## Decision

The MVP will use application-managed authentication.

FastAPI will:

- Register users
- Normalize email addresses
- Hash passwords using a password-specific hashing library
- Validate login credentials
- Issue short-lived JWT access tokens
- Validate tokens on protected requests
- Load the current user from PostgreSQL
- Reject disabled users
- Enforce roles and ownership server-side

Public registration always assigns the `user` role.

Clients cannot assign themselves the `admin` role.

The initial MVP uses access tokens only.

Refresh tokens, revocation, password reset, email verification, multifactor authentication, and enterprise SSO are deferred.

The browser token-storage approach must be reviewed before public deployment, with secure HTTP-only cookies as the preferred production direction.

## Alternatives Considered

### Clerk

Clerk provides fast hosted authentication and a free tier, but it would reduce the opportunity to demonstrate backend authentication logic and introduce a third-party dependency.

### Auth0

Auth0 provides mature identity capabilities but introduces additional configuration, platform dependency, and potential pricing constraints.

### Server-Side Sessions

Sessions offer strong browser security patterns, but distributed session storage and CSRF controls would add complexity to the initial API-first implementation.

### OAuth or OIDC from the Beginning

Enterprise federation is desirable later but is unnecessary for the MVP's two-role portfolio use case.

### API Keys

API keys are not appropriate for interactive user authentication.

## Consequences

### Positive

- No paid identity dependency is required.
- Authentication behavior remains visible and testable in the codebase.
- Demonstrates password hashing, token validation, and RBAC.
- Works across local, low-cost hosted, and Kubernetes deployments.
- Supports stateless API replicas.
- Aligns with FastAPI's security tooling.

### Negative

- The application assumes identity-security responsibilities.
- Token theft and browser storage require careful handling.
- Revocation is limited until additional token controls are added.
- Password reset and email verification are not initially available.
- The implementation must not be described as enterprise-ready authentication.

## Review Conditions

Review this decision before:

- Public production use
- Handling sensitive customer data
- Adding enterprise users
- Requiring SSO or MFA
- Introducing long-lived sessions
- Expanding beyond a portfolio demonstration
- Adding team or organization tenancy
