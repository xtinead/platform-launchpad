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
  max_image_count      = 10
}

module "secrets" {
  source = "../../modules/secrets"

  project_name = var.project_name
  environment  = var.environment

  recovery_window_in_days = 7
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