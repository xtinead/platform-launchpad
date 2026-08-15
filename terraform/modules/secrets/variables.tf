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

variable "recovery_window_in_days" {
  description = "Number of days before a deleted secret is permanently removed."
  type        = number
  default     = 7

  validation {
    condition = (
      var.recovery_window_in_days >= 7 &&
      var.recovery_window_in_days <= 30
    )

    error_message = (
      "recovery_window_in_days must be between 7 and 30."
    )
  }
}