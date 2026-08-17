locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


resource "aws_ecr_repository" "load_balancer_controller" {
  name = (
    "${local.name_prefix}-aws-load-balancer-controller"
  )

  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = merge(
    local.common_tags,
    {
      Name = (
        "${local.name_prefix}-aws-load-balancer-controller"
      )
      Tier = "platform"
    }
  )
}


resource "aws_ecr_lifecycle_policy" "load_balancer_controller" {
  repository = (
    aws_ecr_repository.load_balancer_controller.name
  )

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1

        description = (
          "Retain the five most recent controller images"
        )

        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 5
        }

        action = {
          type = "expire"
        }
      },
    ]
  })
}