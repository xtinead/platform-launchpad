locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


resource "aws_db_subnet_group" "this" {
  name = "${local.name_prefix}-db-subnet-group"

  subnet_ids = var.private_db_subnet_ids

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-db-subnet-group"
      Tier = "database"
    }
  )
}


resource "aws_db_instance" "postgres" {
  identifier = "${local.name_prefix}-postgres"

  engine         = "postgres"
  engine_version = var.engine_version

  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.database_name
  username = var.master_username

  manage_master_user_password = true

  db_subnet_group_name = aws_db_subnet_group.this.name

  vpc_security_group_ids = [
    var.security_group_id,
  ]

  publicly_accessible = false
  multi_az            = false

  backup_retention_period = var.backup_retention_period

  auto_minor_version_upgrade = true

  deletion_protection = var.deletion_protection

  skip_final_snapshot = true

  copy_tags_to_snapshot = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-postgres"
      Tier = "database"
    }
  )
}