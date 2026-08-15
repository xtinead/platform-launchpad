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

variable "private_subnet_ids" {
  description = "Private application subnet IDs used by ElastiCache."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_ids) >= 2
    error_message = "At least two private subnet IDs must be provided."
  }
}

variable "security_group_id" {
  description = "Security group assigned to the Redis replication group."
  type        = string
}

variable "node_type" {
  description = "ElastiCache node type."
  type        = string
  default     = "cache.t4g.micro"
}

variable "engine_version" {
  description = "Redis OSS major engine version."
  type        = string
  default     = "7.1"
}

variable "port" {
  description = "Redis listener port."
  type        = number
  default     = 6379
}