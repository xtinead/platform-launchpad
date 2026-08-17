variable "project_name" {
  description = "Project name used for naming and tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "aws_region" {
  description = "AWS region containing the VPC."
  type        = string
}

variable "vpc_id" {
  description = "VPC ID in which endpoints are created."
  type        = string
}

variable "private_subnet_ids" {
  description = "Private application subnet IDs for interface endpoints."
  type        = list(string)
}

variable "private_route_table_id" {
  description = "Private application route table ID used by the S3 gateway endpoint."
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR allowed to reach interface endpoints."
  type        = string
}