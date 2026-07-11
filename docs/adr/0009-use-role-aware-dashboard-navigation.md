# ADR-0009: Use Role-Aware Dashboard Navigation

## Status

Accepted

## Context

Platform Launchpad supports both regular users and administrators.

Regular users need a focused experience for requesting and managing their own environments. Administrators need additional access to users, all environments, failed operations, status overrides, and audit logs.

Using the same unrestricted navigation for both roles would:

- Expose irrelevant administrative options to regular users
- Increase interface complexity
- Create confusion about available permissions
- Encourage the mistaken assumption that frontend visibility defines authorization

The application needs a clear navigation strategy while preserving backend enforcement as the true security boundary.

## Decision

Platform Launchpad will use role-aware navigation.

Regular users will see:

- Dashboard
- Environments
- Create Environment
- Profile
- Sign Out

Administrators will additionally see:

- Admin Overview
- Users
- All Environments
- Audit Logs

The frontend will derive navigation visibility from the authenticated user's role.

The FastAPI backend will independently authorize every protected operation. Hidden navigation items do not constitute access control.

Unauthorized direct navigation will result in:

- A permission-denied page where appropriate, or
- A not-found response where resource concealment is preferred

## Alternatives Considered

### Show All Navigation to Every User

This was rejected because it creates unnecessary confusion and exposes actions that most users cannot perform.

### Build Separate Applications for Users and Administrators

This was rejected because it introduces duplicate frontend infrastructure and unnecessary maintenance for the MVP.

### Use Frontend Navigation as the Authorization Boundary

This was rejected because client-side controls can be bypassed and cannot provide secure authorization.

## Consequences

### Positive

- Regular-user workflows remain focused.
- Administrative capabilities are easy to find.
- One frontend application supports both roles.
- Navigation aligns with user responsibilities.
- Backend authorization remains explicit.

### Negative

- The frontend must maintain role-aware route and navigation logic.
- Role changes may require refreshing authentication state.
- Automated tests must cover both role experiences.
- Direct-route authorization failures still require clear handling.

## Review Conditions

Review this decision when:

- Additional roles are introduced.
- Team-scoped permissions are added.
- Administrative functionality grows enough to justify a separate application.
- Enterprise identity providers introduce more complex authorization claims.