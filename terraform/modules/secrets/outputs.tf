output "runtime_secret_name" {
  description = "Name of the application runtime secret."
  value       = aws_secretsmanager_secret.runtime.name
}

output "runtime_secret_arn" {
  description = "ARN of the application runtime secret."
  value       = aws_secretsmanager_secret.runtime.arn
}