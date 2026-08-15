variable "project_name" {
  description = "Project name used for resource naming and tagging."
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

variable "vpc_cidr" {
  description = "IPv4 CIDR block assigned to the VPC."
  type        = string
}

variable "availability_zones" {
  description = "Availability zones used for subnet distribution."
  type        = list(string)

  validation {
    condition     = length(var.availability_zones) == 2
    error_message = "Exactly two availability zones must be provided."
  }
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks assigned to public subnets."
  type        = list(string)

  validation {
    condition     = length(var.public_subnet_cidrs) == 2
    error_message = "Exactly two public subnet CIDRs must be provided."
  }
}

variable "private_app_subnet_cidrs" {
  description = "CIDR blocks assigned to private application subnets."
  type        = list(string)

  validation {
    condition = (
      length(var.private_app_subnet_cidrs) == 2
    )

    error_message = (
      "Exactly two private application subnet CIDRs must be provided."
    )
  }
}

variable "private_db_subnet_cidrs" {
  description = "CIDR blocks assigned to private database subnets."
  type        = list(string)

  validation {
    condition = (
      length(var.private_db_subnet_cidrs) == 2
    )

    error_message = (
      "Exactly two private database subnet CIDRs must be provided."
    )
  }
}