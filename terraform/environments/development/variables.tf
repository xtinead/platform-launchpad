variable "aws_region" {
  description = "AWS region for Platform Launchpad resources."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming and tagging."
  type        = string
  default     = "platform-launchpad"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "development"
}

variable "eks_public_access_cidrs" {
  description = "CIDRs permitted to access the development EKS public API."
  type        = list(string)

  validation {
    condition = (
      length(var.eks_public_access_cidrs) > 0 &&
      !contains(var.eks_public_access_cidrs, "0.0.0.0/0")
    )

    error_message = (
      "EKS public API access must use restricted CIDRs."
    )
  }
}