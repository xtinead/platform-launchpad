locals {
  name_prefix = "${var.project_name}-${var.environment}"
}


module "networking" {
  source = "../../modules/networking"

  project_name = var.project_name
  environment  = var.environment

  vpc_cidr = "10.10.0.0/16"

  availability_zones = [
    "us-east-1a",
    "us-east-1b",
  ]

  public_subnet_cidrs = [
    "10.10.0.0/24",
    "10.10.1.0/24",
  ]

  private_app_subnet_cidrs = [
    "10.10.10.0/24",
    "10.10.11.0/24",
  ]

  private_db_subnet_cidrs = [
    "10.10.20.0/24",
    "10.10.21.0/24",
  ]
}

module "security_groups" {
  source = "../../modules/security-groups"

  project_name = var.project_name
  environment  = var.environment

  vpc_id = module.networking.vpc_id

  application_port = 8000
  postgres_port    = 5432
  redis_port       = 6379
}

module "iam" {
  source = "../../modules/iam"

  project_name = var.project_name
  environment  = var.environment
}

module "ecr" {
  source = "../../modules/ecr"

  project_name = var.project_name
  environment  = var.environment

  image_tag_mutability = "IMMUTABLE"
  scan_on_push         = true
  force_delete         = true
  max_image_count      = 10
}

module "ci_delivery_iam" {
  source = "../../modules/ci-delivery-iam"

  project_name          = var.project_name
  environment           = var.environment
  jenkins_force_destroy = true
  ecr_repository_arn    = module.ecr.repository_arn
}

module "secrets" {
  source = "../../modules/secrets"

  project_name = var.project_name
  environment  = var.environment

  recovery_window_in_days = 0
}

module "rds" {
  source = "../../modules/rds"

  project_name = var.project_name
  environment  = var.environment

  private_db_subnet_ids = (
    module.networking.private_db_subnet_ids
  )

  security_group_id = (
    module.security_groups.postgres_security_group_id
  )

  engine_version          = "18"
  instance_class          = "db.t4g.micro"
  allocated_storage       = 20
  max_allocated_storage   = 50
  database_name           = "platform_launchpad"
  master_username         = "platform_admin"
  backup_retention_period = 1
  deletion_protection     = false
}

module "redis" {
  source = "../../modules/redis"

  project_name = var.project_name
  environment  = var.environment

  private_subnet_ids = (
    module.networking.private_app_subnet_ids
  )

  security_group_id = (
    module.security_groups.redis_security_group_id
  )

  node_type      = "cache.t4g.micro"
  engine_version = "7.1"
  port           = 6379
}

module "vpc_endpoints" {
  source = "../../modules/vpc-endpoints"

  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  vpc_id   = module.networking.vpc_id
  vpc_cidr = module.networking.vpc_cidr

  private_subnet_ids = (
    module.networking.private_app_subnet_ids
  )

  private_route_table_id = (
    module.networking.private_app_route_table_id
  )
}

module "eks" {
  source = "../../modules/eks"

  project_name = var.project_name
  environment  = var.environment

  kubernetes_version = "1.35"

  private_subnet_ids = (
    module.networking.private_app_subnet_ids
  )

  cluster_role_arn = module.iam.eks_cluster_role_arn
  node_role_arn    = module.iam.eks_node_role_arn

  admin_principal_arn = (
    "arn:aws:iam::201854077833:role/Engineer"
  )

  public_access_cidrs = var.eks_public_access_cidrs

  node_instance_types = [
    "t3.medium",
  ]

  node_capacity_type = "ON_DEMAND"

  node_desired_size = 2
  node_min_size     = 2
  node_max_size     = 3

  node_disk_size = 20

  depends_on = [
    module.vpc_endpoints,
  ]
}

module "eks_workload_access" {
  source = "../../modules/eks-workload-access"

  project_name = var.project_name
  environment  = var.environment

  eks_security_group_id = (
    module.eks.cluster_security_group_id
  )

  postgres_security_group_id = (
    module.security_groups.postgres_security_group_id
  )

  redis_security_group_id = (
    module.security_groups.redis_security_group_id
  )

  postgres_port = 5432
  redis_port    = 6379
}

module "application_runtime_iam" {
  source = "../../modules/application-runtime-iam"

  project_name = var.project_name
  environment  = var.environment

  cluster_name = module.eks.cluster_name
  namespace    = "platform-launchpad"

  service_account_names = [
    "backend",
    "worker",
  ]

  runtime_secret_arn = module.secrets.runtime_secret_arn
}

module "load_balancer_controller_iam" {
  source = "../../modules/load-balancer-controller-iam"

  project_name = var.project_name
  environment  = var.environment

  cluster_name = module.eks.cluster_name

  namespace            = "kube-system"
  service_account_name = "aws-load-balancer-controller"

  iam_policy_document = file(
    "${path.module}/../../policies/aws-load-balancer-controller.json"
  )
}

module "controller_ecr" {
  source       = "../../modules/controller-ecr"
  force_delete = true
  project_name = var.project_name
  environment  = var.environment
}

module "argocd_ecr" {
  source       = "../../modules/argocd-ecr"
  force_delete = true
  project_name = var.project_name
  environment  = var.environment
}
