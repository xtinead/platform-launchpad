# ADR-0001: Use Platform Launchpad as the Portfolio Application

## Status

Accepted

## Context

The portfolio already demonstrates individual platform capabilities, including:

- AWS and Kubernetes infrastructure
- Terraform
- Jenkins
- GitOps with Argo CD
- Observability
- Networking and security
- Autoscaling
- CI/CD governance

However, the portfolio needs a cohesive application that brings these capabilities together into one end-to-end engineering case study.

A conventional CRUD application would demonstrate application development but would not strongly communicate platform-engineering responsibilities.

The selected application should:

- Be understandable to recruiters and interviewers
- Demonstrate self-service platform concepts
- Exercise the user's AWS, Terraform, Jenkins, Docker, Kubernetes, GitOps, security, and observability skills
- Support a low-cost public demonstration
- Support a production-style AWS deployment
- Produce meaningful architecture and operational documentation

## Decision

Platform Launchpad will be built as the flagship portfolio application.

Platform Launchpad is a self-service Internal Developer Platform demonstration that allows developers to request, view, and manage application environments through a controlled web interface.

The project will demonstrate:

- Full-stack application development
- Multi-user authentication
- Role-based access control
- Environment lifecycle workflows
- Background processing
- Containerization
- CI/CD
- Infrastructure as Code
- GitOps
- Kubernetes
- AWS
- Observability
- Security
- Cost-conscious architecture

The application logic will remain focused enough that platform engineering remains the primary portfolio signal.

## Alternatives Considered

### Generic Task-Management Application

This would be easier to build but would not naturally demonstrate platform self-service, environment lifecycle operations, GitOps, or infrastructure automation.

### E-Commerce Application

This would support microservices and scaling demonstrations but would shift too much attention toward business-domain implementation.

### DevSecOps Pipeline-Only Demonstration

This would highlight CI/CD and security scanning but would not provide a complete user-facing application or platform-product experience.

### Incident-Management Application

This would demonstrate SRE concepts but would overlap heavily with observability work already represented elsewhere in the portfolio.

## Consequences

### Positive

- Creates one cohesive project that connects existing portfolio capabilities.
- Demonstrates product thinking as well as infrastructure implementation.
- Produces credible Senior Platform Engineer interview stories.
- Supports application, platform, security, and operational discussions.
- Gives interviewers a live product they can understand quickly.
- Provides a clear reason to use Jenkins, Terraform, GitOps, Kubernetes, and observability together.

### Negative

- The project has a broad scope.
- Full completion requires application and platform implementation.
- Scope must be actively controlled to avoid becoming an enterprise platform product.
- The project requires substantial documentation and testing.

## Review Conditions

Review this decision when:

- The application scope becomes too large to complete.
- A different portfolio project better demonstrates the target role.
- The platform capabilities no longer map naturally to the application.
- The project becomes difficult to host or demonstrate affordably.
