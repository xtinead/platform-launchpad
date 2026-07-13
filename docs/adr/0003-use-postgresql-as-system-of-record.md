# ADR-0003: Use PostgreSQL as the System of Record

## Status

Accepted

## Context

Platform Launchpad must persist:

- Users
- Environment ownership
- Environment lifecycle state
- Deployment requests
- Audit logs
- Timestamps
- Relationships between users, environments, and operations
- Extensible metadata

The platform requires transactions, referential integrity, uniqueness constraints, indexing, migrations, and reliable querying.

The database must support local Docker development, low-cost hosted environments, and an AWS production-style deployment.

## Decision

PostgreSQL will be the authoritative system of record for Platform Launchpad.

PostgreSQL will store:

- Users
- Environments
- Deployment requests
- Audit logs
- Application metadata

SQLAlchemy 2.0 will provide the backend object-relational mapping.

Alembic will manage schema migrations.

Local development will use PostgreSQL through Docker Compose.

The AWS production-style deployment will use Amazon RDS for PostgreSQL.

Redis may hold temporary queue and coordination data, but it will not become the authoritative source of application state.

## Alternatives Considered

### MySQL

MySQL could support the relational model, but PostgreSQL provides strong JSONB support, constraint behavior, indexing options, and alignment with the selected application stack.

### SQLite

SQLite would simplify initial development but would not represent the concurrency, deployment, and operational characteristics of the intended hosted architecture.

### DynamoDB

DynamoDB offers managed scalability but would complicate relational ownership, lifecycle history, filtering, transactions, and the audit model.

### MongoDB

MongoDB provides flexible documents but would weaken relational integrity and make ownership and lifecycle constraints more dependent on application logic.

### Redis as Primary Storage

Redis is suitable for queues and caching but not for the durable relational history required by the application.

## Consequences

### Positive

- Strong transactional consistency.
- Foreign-key and uniqueness enforcement.
- Mature migration tooling.
- Excellent SQLAlchemy support.
- JSONB is available for controlled extensible metadata.
- Local and AWS deployment models are straightforward.
- RDS provides managed backups and operational features.
- The data model remains easy to explain and inspect.

### Negative

- PostgreSQL must be operated and secured.
- RDS introduces ongoing AWS cost.
- Schema migrations require planning.
- Connection pooling must be configured correctly.
- Scaling writes requires more planning than a fully distributed datastore.

## Review Conditions

Review this decision when:

- Workload volume exceeds the practical PostgreSQL design.
- A specific workload requires a specialized datastore.
- Audit data requires archival to lower-cost storage.
- Multi-region active-active persistence becomes necessary.
- A managed application platform imposes a different datastore constraint.
