locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# -------------------------------------------------------------------
# ElastiCache Subnet Group
# -------------------------------------------------------------------

resource "aws_elasticache_subnet_group" "this" {
  name = "${local.name_prefix}-redis-subnet-group"

  subnet_ids = var.private_subnet_ids

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-redis-subnet-group"
      Tier = "cache"
    }
  )
}


# -------------------------------------------------------------------
# Redis Replication Group
# -------------------------------------------------------------------

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = "${local.name_prefix}-redis"

  description = (
    "Redis cache for Platform Launchpad ${var.environment}."
  )

  engine         = "redis"
  engine_version = var.engine_version

  node_type = var.node_type
  port      = var.port

  num_cache_clusters = 1

  automatic_failover_enabled = false
  multi_az_enabled           = false

  subnet_group_name = (
    aws_elasticache_subnet_group.this.name
  )

  security_group_ids = [
    var.security_group_id,
  ]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  apply_immediately = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-redis"
      Tier = "cache"
    }
  )
}