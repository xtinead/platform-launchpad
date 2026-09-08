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

variable "ecr_repository_arn" {
  description = "ARN of the ECR repository CI may publish to."
  type        = string
}

variable "jenkins_force_destroy" {
  description = "Allow deletion of the Jenkins IAM user when access keys or other credentials remain."
  type        = bool
  default     = false
}