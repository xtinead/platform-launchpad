locals {
  name_prefix = "${var.project_name}/${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


resource "aws_secretsmanager_secret" "runtime" {
  name = "${local.name_prefix}/runtime"

  description = (
    "Runtime secrets for Platform Launchpad application workloads."
  )

  recovery_window_in_days = var.recovery_window_in_days

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-runtime-secret"
      Tier = "application"
    }
  )
}