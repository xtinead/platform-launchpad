output "alb_security_group_id" {
  description = "Security group ID for the public ALB."
  value       = aws_security_group.alb.id
}

output "application_security_group_id" {
  description = "Security group ID for application workloads."
  value       = aws_security_group.application.id
}

output "postgres_security_group_id" {
  description = "Security group ID for PostgreSQL."
  value       = aws_security_group.postgres.id
}

output "redis_security_group_id" {
  description = "Security group ID for Redis."
  value       = aws_security_group.redis.id
}