# ADR-0013: Use OpenTelemetry for Distributed Tracing

## Status

Accepted

## Context

Platform Launchpad includes several components that participate in one user workflow:

- Next.js frontend
- FastAPI backend
- PostgreSQL
- Redis
- Python worker
- Future Jenkins and platform integrations

A single environment request may cross HTTP requests, database operations, queue publication, worker execution, and infrastructure APIs.

Logs alone make it difficult to reconstruct the entire workflow, especially when operations are asynchronous.

The project needs a vendor-neutral tracing approach that can correlate activity across services.

## Decision

Platform Launchpad will use OpenTelemetry for distributed tracing.

OpenTelemetry instrumentation will be introduced incrementally for:

1. FastAPI incoming requests
2. Outbound HTTP calls
3. SQLAlchemy database operations
4. Redis queue publication
5. Worker task execution
6. Frontend API requests where practical

Trace context should propagate through HTTP headers and worker-task metadata.

Tempo is the preferred initial trace backend for the Kubernetes observability stack.

Trace identifiers will be included in structured logs.

## Alternatives Considered

### Logs Only

Rejected because reconstructing asynchronous cross-service workflows would be difficult and time-consuming.

### Vendor-Specific Instrumentation

Rejected because it would tightly couple the application to one observability provider.

### Custom Correlation IDs Without Tracing

Request IDs remain useful, but they do not provide span timing, dependency hierarchy, or distributed context.

### Defer Tracing Entirely

Rejected because environment lifecycle workflows are a core portfolio capability and benefit significantly from trace visualization.

## Consequences

### Positive

- End-to-end request visibility
- Vendor-neutral instrumentation
- Correlation between logs and traces
- Better asynchronous workflow troubleshooting
- Visibility into database and queue latency
- Stronger observability demonstration for interviews

### Negative

- Additional instrumentation complexity
- Additional runtime overhead
- Trace storage cost
- Queue context propagation requires deliberate implementation
- Sampling configuration must be managed

## Review Conditions

Review this decision when:

- A managed observability platform is adopted.
- Trace volume becomes too expensive.
- A service mesh provides sufficient tracing.
- OpenTelemetry support changes materially.
- The application architecture becomes significantly simpler.