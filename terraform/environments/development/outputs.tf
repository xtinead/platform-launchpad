output "environment" {
  description = "Current Terraform environment."
  value       = var.environment
}

output "aws_region" {
  description = "AWS region used by this environment."
  value       = var.aws_region
}

output "name_prefix" {
  description = "Resource naming prefix."
  value       = local.name_prefix
}

output "vpc_id" {
  description = "Development VPC ID."
  value       = module.networking.vpc_id
}

output "public_subnet_ids" {
  description = "Development public subnet IDs."
  value       = module.networking.public_subnet_ids
}

output "private_app_subnet_ids" {
  description = "Development private application subnet IDs."
  value       = module.networking.private_app_subnet_ids
}

output "private_db_subnet_ids" {
  description = "Development private database subnet IDs."
  value       = module.networking.private_db_subnet_ids
}

output "alb_security_group_id" {
  description = "Development ALB security group ID."
  value       = module.security_groups.alb_security_group_id
}

output "application_security_group_id" {
  description = "Development application security group ID."
  value       = module.security_groups.application_security_group_id
}

output "postgres_security_group_id" {
  description = "Development PostgreSQL security group ID."
  value       = module.security_groups.postgres_security_group_id
}

output "redis_security_group_id" {
  description = "Development Redis security group ID."
  value       = module.security_groups.redis_security_group_id
}

output "eks_cluster_role_arn" {
  description = "Development EKS cluster IAM role ARN."
  value       = module.iam.eks_cluster_role_arn
}

output "eks_node_role_arn" {
  description = "Development EKS node IAM role ARN."
  value       = module.iam.eks_node_role_arn
}

output "worker_role_arn" {
  description = "Development platform worker IAM role ARN."
  value       = module.iam.worker_role_arn
}

output "worker_policy_arn" {
  description = "Development platform worker policy ARN."
  value       = module.iam.worker_policy_arn
}

output "ecr_repository_name" {
  description = "Development application ECR repository name."
  value       = module.ecr.repository_name
}

output "ecr_repository_arn" {
  description = "Development application ECR repository ARN."
  value       = module.ecr.repository_arn
}

output "ecr_repository_url" {
  description = "Development application ECR repository URL."
  value       = module.ecr.repository_url
}

output "runtime_secret_name" {
  description = "Development runtime secret name."
  value       = module.secrets.runtime_secret_name
}

output "runtime_secret_arn" {
  description = "Development runtime secret ARN."
  value       = module.secrets.runtime_secret_arn
}

output "rds_endpoint" {
  description = "Development PostgreSQL endpoint."
  value       = module.rds.db_endpoint
}

output "rds_instance_arn" {
  description = "Development PostgreSQL instance ARN."
  value       = module.rds.db_instance_arn
}

output "rds_master_user_secret_arn" {
  description = "RDS-managed master credential secret ARN."
  value       = module.rds.master_user_secret_arn
}

output "redis_replication_group_arn" {
  description = "Development Redis replication group ARN."
  value       = module.redis.replication_group_arn
}

output "redis_endpoint" {
  description = "Development Redis primary endpoint."
  value       = module.redis.primary_endpoint_address
}

output "redis_port" {
  description = "Development Redis port."
  value       = module.redis.port
}