locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


resource "aws_iam_user" "jenkins" {
  name = "${local.name_prefix}-jenkins"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-jenkins"
      Tier = "delivery"
    }
  )
}


data "aws_iam_policy_document" "assume_role" {
  statement {
    sid    = "AllowJenkinsBootstrapPrincipal"
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type = "AWS"

      identifiers = [
        aws_iam_user.jenkins.arn,
      ]
    }
  }
}


resource "aws_iam_role" "ci_delivery" {
  name = "${local.name_prefix}-ci-delivery"

  description = (
    "Least-privilege CI delivery role for Platform Launchpad."
  )

  assume_role_policy = (
    data.aws_iam_policy_document.assume_role.json
  )

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ci-delivery"
      Tier = "delivery"
    }
  )
}


data "aws_iam_policy_document" "jenkins_assume_role" {
  statement {
    sid    = "AllowCIDeliveryRoleAssumption"
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
    ]

    resources = [
      aws_iam_role.ci_delivery.arn,
    ]
  }
}


resource "aws_iam_policy" "jenkins_assume_role" {
  name = "${local.name_prefix}-jenkins-assume-ci-delivery"

  description = (
    "Allows Jenkins to assume the Platform Launchpad CI delivery role."
  )

  policy = (
    data.aws_iam_policy_document.jenkins_assume_role.json
  )

  tags = local.common_tags
}


resource "aws_iam_user_policy_attachment" "jenkins_assume_role" {
  user       = aws_iam_user.jenkins.name
  policy_arn = aws_iam_policy.jenkins_assume_role.arn
}


data "aws_iam_policy_document" "ecr_publish" {
  statement {
    sid    = "AllowECRAuthentication"
    effect = "Allow"

    actions = [
      "ecr:GetAuthorizationToken",
    ]

    resources = [
      "*",
    ]
  }

  statement {
    sid    = "AllowApplicationImagePublication"
    effect = "Allow"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:DescribeImages",
      "ecr:DescribeRepositories",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:ListImages",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]

    resources = [
      var.ecr_repository_arn,
    ]
  }
}


resource "aws_iam_policy" "ecr_publish" {
  name = "${local.name_prefix}-ci-delivery"

  description = (
    "Allows Platform Launchpad CI to publish application images to ECR."
  )

  policy = data.aws_iam_policy_document.ecr_publish.json

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ci-delivery"
      Tier = "delivery"
    }
  )
}


resource "aws_iam_role_policy_attachment" "ecr_publish" {
  role       = aws_iam_role.ci_delivery.name
  policy_arn = aws_iam_policy.ecr_publish.arn
}