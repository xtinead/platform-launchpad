variable "project_name" {
  description = "Project name used for naming and tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "force_delete" {
  description = "Allow the controller ECR repository to be deleted even when images remain."
  type        = bool
  default     = false
}