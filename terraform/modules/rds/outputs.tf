output "db_instance_id" {
  description = "RDS PostgreSQL instance identifier."
  value       = aws_db_instance.postgres.id
}

output "db_instance_arn" {
  description = "RDS PostgreSQL instance ARN."
  value       = aws_db_instance.postgres.arn
}

output "db_endpoint" {
  description = "RDS PostgreSQL connection endpoint."
  value       = aws_db_instance.postgres.endpoint
}

output "db_address" {
  description = "RDS PostgreSQL hostname."
  value       = aws_db_instance.postgres.address
}

output "db_port" {
  description = "RDS PostgreSQL port."
  value       = aws_db_instance.postgres.port
}

output "master_user_secret_arn" {
  description = "ARN of the RDS-managed master credential secret."
  value       = aws_db_instance.postgres.master_user_secret[0].secret_arn
}