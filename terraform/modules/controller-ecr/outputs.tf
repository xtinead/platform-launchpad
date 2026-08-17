output "repository_name" {
  description = "Controller ECR repository name."
  value = (
    aws_ecr_repository.load_balancer_controller.name
  )
}

output "repository_url" {
  description = "Controller ECR repository URL."
  value = (
    aws_ecr_repository.load_balancer_controller.repository_url
  )
}

output "repository_arn" {
  description = "Controller ECR repository ARN."
  value = (
    aws_ecr_repository.load_balancer_controller.arn
  )
}