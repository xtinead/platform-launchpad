locals {
  name_prefix = "${var.project_name}-${var.environment}"

  repositories = {
    argocd = {
      suffix = "argocd"
    }

    dex = {
      suffix = "argocd-dex"
    }

    redis = {
      suffix = "argocd-redis"
    }
  }

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Tier        = "platform"
  }
}

resource "aws_ecr_repository" "this" {
  for_each = local.repositories

  name = (
    "${local.name_prefix}-${each.value.suffix}"
  )
  force_delete         = var.force_delete
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
        "${local.name_prefix}-${each.value.suffix}"
      )
    }
  )
}

resource "aws_ecr_lifecycle_policy" "this" {
  for_each = aws_ecr_repository.this

  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1

        description = (
          "Retain the five most recent bootstrap images"
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