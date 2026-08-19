variable "project_name" {
  description = "Project name used for tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string

  validation {
    condition = contains(
      ["development", "staging", "production"],
      var.environment
    )

    error_message = (
      "Environment must be development, staging, or production."
    )
  }
}

variable "eks_security_group_id" {
  description = "Security group used by EKS workload ENIs."
  type        = string
}

variable "postgres_security_group_id" {
  description = "Security group protecting PostgreSQL."
  type        = string
}

variable "redis_security_group_id" {
  description = "Security group protecting Redis."
  type        = string
}

variable "postgres_port" {
  description = "PostgreSQL listener port."
  type        = number
  default     = 5432
}

variable "redis_port" {
  description = "Redis listener port."
  type        = number
  default     = 6379
}