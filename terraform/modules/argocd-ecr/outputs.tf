output "repository_names" {
  description = "Argo CD bootstrap ECR repository names."

  value = {
    for key, repository in aws_ecr_repository.this :
    key => repository.name
  }
}

output "repository_urls" {
  description = "Argo CD bootstrap ECR repository URLs."

  value = {
    for key, repository in aws_ecr_repository.this :
    key => repository.repository_url
  }
}