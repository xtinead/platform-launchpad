output "replication_group_id" {
  description = "Redis replication group identifier."
  value       = aws_elasticache_replication_group.redis.id
}

output "replication_group_arn" {
  description = "Redis replication group ARN."
  value       = aws_elasticache_replication_group.redis.arn
}

output "primary_endpoint_address" {
  description = "Primary Redis endpoint hostname."
  value = (
    aws_elasticache_replication_group.redis.primary_endpoint_address
  )
}

output "port" {
  description = "Redis listener port."
  value       = aws_elasticache_replication_group.redis.port
}

output "subnet_group_name" {
  description = "ElastiCache subnet group name."
  value       = aws_elasticache_subnet_group.this.name
}