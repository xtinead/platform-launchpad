# ADR-0008: Preserve Environment History with Logical Destruction

## Status

Accepted

## Context

Platform Launchpad environments represent both active platform resources and historical user activity.

Physically deleting an environment database record when infrastructure is destroyed would remove useful information needed for:

- Auditing
- Troubleshooting
- Reporting
- Deployment history
- Interview demonstrations
- Future compliance requirements

The platform needs a consistent approach for environment deletion.

## Decision

Environment destruction will be implemented as a lifecycle operation rather than immediate database deletion.

When an environment is destroyed:

1. Its status changes to `destroying`.
2. A deployment request records the destruction operation.
3. The worker performs infrastructure cleanup.
4. Its status changes to `destroyed`.
5. The `destroyed_at` timestamp is recorded.
6. The environment record remains in PostgreSQL.

The MVP will not expose a standard API endpoint that physically deletes environment records.

## Alternatives Considered

### Hard Delete Immediately

The environment record could be deleted after infrastructure cleanup.

This was rejected because it removes operational history and weakens auditability.

### Generic `deleted_at` Soft Delete

The platform could add a generic `deleted_at` field and hide deleted rows.

This was not selected for the MVP because environment destruction is a meaningful domain lifecycle state and should remain explicitly visible.

### Archive to a Separate Table

Destroyed environments could be moved to an archive table.

This adds unnecessary complexity for the MVP and makes historical querying more difficult.

## Consequences

### Positive

- Preserves complete environment history.
- Supports audit and troubleshooting workflows.
- Makes lifecycle reporting easier.
- Avoids accidental loss of operational records.
- Allows failed destruction workflows to remain visible.

### Negative

- Application queries must distinguish active and destroyed environments.
- Database size grows over time.
- A future retention and archival policy may be required.
- Environment-name uniqueness requires careful handling.

## Review Conditions

Review this decision when:

- Storage growth becomes significant.
- Regulatory retention requirements are introduced.
- Users require permanent data erasure.
- Archived records need to move to lower-cost storage.