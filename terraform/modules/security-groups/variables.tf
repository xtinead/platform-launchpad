variable "project_name" {
  description = "Project name used for naming and tagging."
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

variable "vpc_id" {
  description = "VPC in which security groups will be created."
  type        = string
}

variable "application_port" {
  description = "Backend application port exposed to the load balancer."
  type        = number
  default     = 8000
}

variable "postgres_port" {
  description = "PostgreSQL database port."
  type        = number
  default     = 5432
}

variable "redis_port" {
  description = "Redis port."
  type        = number
  default     = 6379
}