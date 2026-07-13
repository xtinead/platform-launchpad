# ADR-0002: Use Next.js and FastAPI for the Application

## Status

Accepted

## Context

Platform Launchpad requires:

- A browser-based developer portal
- A REST API
- Authentication and authorization
- Environment lifecycle operations
- Integration with PostgreSQL
- Background task submission
- Health and metrics endpoints
- Strong API documentation
- Straightforward containerization

The application stack should be modern, understandable in interviews, productive for development, and suitable for deployment to both low-cost hosting platforms and Kubernetes.

## Decision

Platform Launchpad will use:

- Next.js with TypeScript for the frontend
- FastAPI with Python for the backend API
- Python for the background worker

Next.js will provide:

- React-based UI development
- TypeScript
- Routing
- Server and client rendering options
- Good deployment support
- A strong ecosystem for dashboards and forms

FastAPI will provide:

- Typed API development
- Pydantic validation
- Automatic OpenAPI generation
- Dependency injection
- Async support
- Straightforward testing
- Health and metrics endpoints
- Python compatibility with the worker and automation code

The frontend will communicate only with FastAPI and will not access PostgreSQL, Redis, Jenkins, Kubernetes, or AWS directly.

## Alternatives Considered

### React with Express

This would keep the entire application in JavaScript or TypeScript, but FastAPI offers stronger alignment with the project's Python automation and worker requirements.

### Django

Django provides mature authentication and ORM features but introduces more framework structure than required for this API-focused application.

### Flask

Flask is lightweight but requires more manual assembly for validation, OpenAPI documentation, dependency injection, and typed request handling.

### Next.js Full-Stack Only

Using Next.js for both frontend and backend could simplify deployment, but it would reduce the opportunity to demonstrate a separate API service, Python worker, service boundaries, and independent scaling.

### Java or Spring Boot

This would provide enterprise credibility but would significantly increase development effort and reduce delivery speed for this portfolio project.

## Consequences

### Positive

- Clear separation between frontend and backend.
- Strong type support across both application layers.
- FastAPI maps naturally to the OpenAPI-first design.
- Python can be reused for the API, worker, tests, and automation.
- Both services containerize cleanly.
- Frontend and backend can scale independently.
- The stack is easy to host on low-cost platforms.
- The architecture provides strong interview discussion points.

### Negative

- Two language ecosystems must be maintained.
- Authentication state must be coordinated between Next.js and FastAPI.
- Cross-origin configuration is required when services use separate domains.
- Separate dependency and testing toolchains are required.
- Deployment involves multiple container images.

## Review Conditions

Review this decision when:

- The frontend and backend deployment model becomes unnecessarily complex.
- Team expertise strongly favors another stack.
- A Backend-for-Frontend layer becomes necessary.
- Performance requirements exceed the selected framework capabilities.
- The application becomes better suited to a single full-stack framework.
