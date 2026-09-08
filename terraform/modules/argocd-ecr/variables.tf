variable "project_name" {
  description = "Project name used for naming and tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "force_delete" {
  description = "Allow Argo CD bootstrap ECR repositories to be deleted even when images remain."
  type        = bool
  default     = false
}