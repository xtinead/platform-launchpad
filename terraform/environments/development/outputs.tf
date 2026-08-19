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

output "vpc_endpoint_security_group_id" {
  description = "Development VPC endpoint security group."
  value       = module.vpc_endpoints.endpoint_security_group_id
}

output "ecr_api_endpoint_id" {
  description = "Development ECR API endpoint."
  value       = module.vpc_endpoints.ecr_api_endpoint_id
}

output "ecr_dkr_endpoint_id" {
  description = "Development ECR Docker endpoint."
  value       = module.vpc_endpoints.ecr_dkr_endpoint_id
}

output "ec2_endpoint_id" {
  description = "Development EC2 endpoint."
  value       = module.vpc_endpoints.ec2_endpoint_id
}

output "s3_endpoint_id" {
  description = "Development S3 gateway endpoint."
  value       = module.vpc_endpoints.s3_endpoint_id
}

output "eks_endpoint_id" {
  description = "Development Amazon EKS API endpoint."
  value       = module.vpc_endpoints.eks_endpoint_id
}

output "eks_cluster_name" {
  description = "Development EKS cluster name."
  value       = module.eks.cluster_name
}

output "eks_cluster_arn" {
  description = "Development EKS cluster ARN."
  value       = module.eks.cluster_arn
}

output "eks_cluster_endpoint" {
  description = "Development EKS Kubernetes API endpoint."
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_version" {
  description = "Development EKS Kubernetes version."
  value       = module.eks.cluster_version
}

output "eks_cluster_security_group_id" {
  description = "Development EKS cluster security group."
  value       = module.eks.cluster_security_group_id
}

output "eks_node_group_name" {
  description = "Development EKS managed node group name."
  value       = module.eks.node_group_name
}

output "eks_node_group_status" {
  description = "Development EKS managed node group status."
  value       = module.eks.node_group_status
}

output "eks_auth_endpoint_id" {
  description = "Development Amazon EKS Auth API endpoint."
  value       = module.vpc_endpoints.eks_auth_endpoint_id
}

output "elasticloadbalancing_endpoint_id" {
  description = "Development Elastic Load Balancing API endpoint."
  value = (
    module.vpc_endpoints.elasticloadbalancing_endpoint_id
  )
}

output "load_balancer_controller_repository_name" {
  description = "AWS Load Balancer Controller ECR repository name."
  value       = module.controller_ecr.repository_name
}

output "load_balancer_controller_repository_url" {
  description = "AWS Load Balancer Controller ECR repository URL."
  value       = module.controller_ecr.repository_url
}

output "load_balancer_controller_role_arn" {
  description = "AWS Load Balancer Controller Pod Identity role ARN."
  value       = module.load_balancer_controller_iam.role_arn
}

output "load_balancer_controller_policy_arn" {
  description = "AWS Load Balancer Controller IAM policy ARN."
  value       = module.load_balancer_controller_iam.policy_arn
}

output "load_balancer_controller_pod_identity_association_id" {
  description = "AWS Load Balancer Controller Pod Identity association ID."
  value = (
    module.load_balancer_controller_iam.association_id
  )
}

output "eks_postgres_ingress_rule_id" {
  description = "Rule allowing EKS workloads to access PostgreSQL."
  value = (
    module.eks_workload_access.postgres_ingress_rule_id
  )
}

output "eks_redis_ingress_rule_id" {
  description = "Rule allowing EKS workloads to access Redis."
  value = (
    module.eks_workload_access.redis_ingress_rule_id
  )
}

output "secretsmanager_endpoint_id" {
  description = "Secrets Manager interface VPC endpoint ID."
  value       = module.vpc_endpoints.secretsmanager_endpoint_id
}

output "application_runtime_role_arn" {
  description = "Application runtime Pod Identity role ARN."
  value       = module.application_runtime_iam.role_arn
}

output "application_runtime_policy_arn" {
  description = "Application runtime Secrets Manager policy ARN."
  value       = module.application_runtime_iam.policy_arn
}

output "application_runtime_pod_identity_association_ids" {
  description = "Application runtime Pod Identity association IDs."
  value = (
    module.application_runtime_iam.pod_identity_association_ids
  )
}