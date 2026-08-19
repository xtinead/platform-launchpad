locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# -------------------------------------------------------------------
# EKS Pod Identity Trust Policy
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
# Runtime Secret Permissions
# -------------------------------------------------------------------

data "aws_iam_policy_document" "runtime_secrets" {
  statement {
    sid    = "ReadRuntimeSecret"
    effect = "Allow"

    actions = [
      "secretsmanager:DescribeSecret",
      "secretsmanager:GetSecretValue",
    ]

    resources = [
      var.runtime_secret_arn,
    ]
  }
}


resource "aws_iam_policy" "runtime_secrets" {
  name = "${local.name_prefix}-application-runtime-secrets-policy"

  description = (
    "Read access to Platform Launchpad application runtime secrets."
  )

  policy = data.aws_iam_policy_document.runtime_secrets.json

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-application-runtime-secrets-policy"
      Tier = "application"
    }
  )
}


# -------------------------------------------------------------------
# Application Runtime Pod Identity Role
# -------------------------------------------------------------------

resource "aws_iam_role" "runtime" {
  name = "${local.name_prefix}-application-runtime-role"

  assume_role_policy = (
    data.aws_iam_policy_document.assume_role.json
  )

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-application-runtime-role"
      Tier = "application"
    }
  )
}


resource "aws_iam_role_policy_attachment" "runtime_secrets" {
  role       = aws_iam_role.runtime.name
  policy_arn = aws_iam_policy.runtime_secrets.arn
}


# -------------------------------------------------------------------
# EKS Pod Identity Associations
# -------------------------------------------------------------------

resource "aws_eks_pod_identity_association" "runtime" {
  for_each = var.service_account_names

  cluster_name = var.cluster_name

  namespace       = var.namespace
  service_account = each.value

  role_arn = aws_iam_role.runtime.arn

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-${each.value}-pod-identity"
      Tier = "application"
    }
  )

  depends_on = [
    aws_iam_role_policy_attachment.runtime_secrets,
  ]
}