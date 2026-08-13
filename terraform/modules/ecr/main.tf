locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


resource "aws_ecr_repository" "application" {
  name = "${local.name_prefix}-application"

  image_tag_mutability = var.image_tag_mutability

  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-application"
      Tier = "application"
    }
  )
}


resource "aws_ecr_lifecycle_policy" "application" {
  repository = aws_ecr_repository.application.name

  policy = jsonencode(
    {
      rules = [
        {
          rulePriority = 1
          description  = "Expire old untagged images"

          selection = {
            tagStatus   = "untagged"
            countType   = "imageCountMoreThan"
            countNumber = var.max_image_count
          }

          action = {
            type = "expire"
          }
        }
      ]
    }
  )
}