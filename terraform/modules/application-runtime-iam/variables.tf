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

variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
}

variable "namespace" {
  description = "Kubernetes namespace containing application workloads."
  type        = string
}

variable "service_account_names" {
  description = "Kubernetes service accounts granted runtime secret access."
  type        = set(string)
}

variable "runtime_secret_arn" {
  description = "Secrets Manager ARN containing application runtime secrets."
  type        = string
}