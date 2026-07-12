# ADR-0011: Use Immutable Container Image Digests for Deployment

## Status

Accepted

## Context

Platform Launchpad publishes frontend, backend, and worker container images to Amazon ECR.

Container tags such as `latest`, `development`, or even semantic-version tags can be overwritten unless registry controls prevent mutation. A mutable reference can make it difficult to prove which exact artifact is running.

The platform needs:

- Reproducible deployments
- Reliable rollback
- Supply-chain traceability
- Clear mapping from source code to runtime
- Protection from accidental tag replacement

## Decision

Platform Launchpad will use container image digests as the authoritative deployment identifier.

The CI pipeline will:

1. Build the application image.
2. Apply human-readable tags.
3. Push the image to Amazon ECR.
4. Capture the published SHA-256 digest.
5. Update the GitOps repository with the digest.
6. Preserve source and build metadata.

Example:

```yaml
images:
  - name: platform-launchpad-backend
    newName: 201854077833.dkr.ecr.us-east-1.amazonaws.com/platform-launchpad-backend
    digest: sha256:1234567890abcdef
```

Human-readable tags remain available for operators, but Argo CD deployment state should resolve to an immutable image identity.

## Alternatives Considered

### Deploy Using `latest`

Rejected because `latest` is mutable, ambiguous, and unsuitable for reliable rollback.

### Deploy Using Jenkins Build Tags Only

Build tags improve traceability but may still be mutable unless registry immutability is enforced.

### Deploy Using Semantic Versions Only

Semantic versions are useful for releases but can still be overwritten accidentally without additional controls.

### Rebuild Images for Each Environment

Rejected because development, staging, and production could receive different artifacts despite referencing the same source version.

## Consequences

### Positive

- Runtime artifacts are immutable.
- Rollback identifies an exact known-good image.
- GitOps history accurately identifies deployed content.
- Source-to-runtime traceability improves.
- Tag replacement does not silently alter desired state.
- The same artifact can be promoted between environments.

### Negative

- Digests are less readable than tags.
- Pipeline logic must capture and update digest values.
- Operators need tooling to correlate digests with release versions.
- Multi-architecture manifests require careful digest handling.

## Review Conditions

Review this decision when:

- Image signing is introduced.
- Provenance attestations are enforced.
- A release-management platform provides stronger artifact identity.
- Deployment tooling changes from Kubernetes and Argo CD.