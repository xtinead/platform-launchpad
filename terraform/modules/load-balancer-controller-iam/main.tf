locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# -------------------------------------------------------------------
# Pod Identity Trust Policy
# -------------------------------------------------------------------

data "aws_iam_policy_document" "assume_role" {
  statement {
    sid    = "AllowEksPodIdentity"
    effect = "Allow"

    principals {
      type = "Service"

      identifiers = [
        "pods.eks.amazonaws.com",
      ]
    }

    actions = [
      "sts:AssumeRole",
      "sts:TagSession",
    ]
  }
}


# -------------------------------------------------------------------
# AWS Load Balancer Controller IAM Policy
# -------------------------------------------------------------------

resource "aws_iam_policy" "controller" {
  name = (
    "${local.name_prefix}-load-balancer-controller-policy"
  )

  description = (
    "Permissions for the AWS Load Balancer Controller."
  )

  policy = var.iam_policy_document

  tags = merge(
    local.common_tags,
    {
      Name = (
        "${local.name_prefix}-load-balancer-controller-policy"
      )
      Tier = "platform"
    }
  )
}


# -------------------------------------------------------------------
# AWS Load Balancer Controller Pod Identity Role
# -------------------------------------------------------------------

resource "aws_iam_role" "controller" {
  name = (
    "${local.name_prefix}-load-balancer-controller-role"
  )

  assume_role_policy = (
    data.aws_iam_policy_document.assume_role.json
  )

  tags = merge(
    local.common_tags,
    {
      Name = (
        "${local.name_prefix}-load-balancer-controller-role"
      )
      Tier = "platform"
    }
  )
}


resource "aws_iam_role_policy_attachment" "controller" {
  role       = aws_iam_role.controller.name
  policy_arn = aws_iam_policy.controller.arn
}


# -------------------------------------------------------------------
# EKS Pod Identity Association
# -------------------------------------------------------------------

resource "aws_eks_pod_identity_association" "controller" {
  cluster_name = var.cluster_name

  namespace = var.namespace

  service_account = var.service_account_name

  role_arn = aws_iam_role.controller.arn

  tags = merge(
    local.common_tags,
    {
      Name = (
        "${local.name_prefix}-load-balancer-controller"
      )
      Tier = "platform"
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.controller,
  ]
}