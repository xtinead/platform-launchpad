from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class EnvironmentType(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    DEMO = "demo"


class EnvironmentStatus(StrEnum):
    PENDING = "pending"
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    FAILED = "failed"
    DESTROYING = "destroying"
    DESTROYED = "destroyed"


class DeploymentOperation(StrEnum):
    PROVISION = "provision"
    DESTROY = "destroy"
    RETRY = "retry"
    UPGRADE = "upgrade"


class DeploymentRequestStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AuditResult(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"