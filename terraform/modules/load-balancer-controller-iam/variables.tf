variable "project_name" {
  description = "Project name used for naming and tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
}

variable "namespace" {
  description = "Kubernetes namespace containing the controller."
  type        = string
  default     = "kube-system"
}

variable "service_account_name" {
  description = "Kubernetes service account used by the controller."
  type        = string
  default     = "aws-load-balancer-controller"
}

variable "iam_policy_document" {
  description = "IAM policy JSON for the AWS Load Balancer Controller."
  type        = string
}