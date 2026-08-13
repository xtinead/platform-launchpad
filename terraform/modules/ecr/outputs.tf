output "repository_name" {
  description = "Name of the Platform Launchpad application repository."
  value       = aws_ecr_repository.application.name
}

output "repository_arn" {
  description = "ARN of the application ECR repository."
  value       = aws_ecr_repository.application.arn
}

output "repository_url" {
  description = "URL used to push and pull application container images."
  value       = aws_ecr_repository.application.repository_url
}

output "registry_id" {
  description = "AWS registry ID that owns the repository."
  value       = aws_ecr_repository.application.registry_id
}