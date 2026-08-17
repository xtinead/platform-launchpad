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

variable "kubernetes_version" {
  description = "Kubernetes version used by the EKS cluster."
  type        = string
  default     = "1.35"
}

variable "private_subnet_ids" {
  description = "Private subnet IDs used by the EKS cluster and node group."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_ids) >= 2
    error_message = "At least two private subnet IDs must be provided."
  }
}

variable "cluster_role_arn" {
  description = "IAM role ARN used by the EKS control plane."
  type        = string
}

variable "node_role_arn" {
  description = "IAM role ARN used by the EKS managed node group."
  type        = string
}

variable "admin_principal_arn" {
  description = "IAM principal granted EKS cluster administrator access."
  type        = string
}

variable "public_access_cidrs" {
  description = "CIDR blocks permitted to reach the public Kubernetes API endpoint."
  type        = list(string)

  validation {
    condition = (
      length(var.public_access_cidrs) > 0 &&
      !contains(var.public_access_cidrs, "0.0.0.0/0")
    )

    error_message = (
      "At least one restricted CIDR must be supplied; 0.0.0.0/0 is not permitted."
    )
  }
}

variable "node_instance_types" {
  description = "EC2 instance types used by the managed node group."
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_capacity_type" {
  description = "Capacity type for the EKS managed node group."
  type        = string
  default     = "ON_DEMAND"

  validation {
    condition = contains(
      ["ON_DEMAND", "SPOT"],
      var.node_capacity_type
    )

    error_message = "Capacity type must be ON_DEMAND or SPOT."
  }
}

variable "node_desired_size" {
  description = "Desired number of managed worker nodes."
  type        = number
  default     = 1
}

variable "node_min_size" {
  description = "Minimum number of managed worker nodes."
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of managed worker nodes."
  type        = number
  default     = 2
}

variable "node_disk_size" {
  description = "Root EBS volume size in GiB for managed worker nodes."
  type        = number
  default     = 20
}