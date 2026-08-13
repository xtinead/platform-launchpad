locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# -------------------------------------------------------------------
# EKS Cluster Role
# -------------------------------------------------------------------

data "aws_iam_policy_document" "eks_cluster_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole",
    ]
  }
}


resource "aws_iam_role" "eks_cluster" {
  name = "${local.name_prefix}-eks-cluster-role"

  assume_role_policy = (
    data.aws_iam_policy_document.eks_cluster_assume_role.json
  )

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-eks-cluster-role"
      Tier = "platform"
    }
  )
}


resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  role = aws_iam_role.eks_cluster.name

  policy_arn = (
    "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  )
}


# -------------------------------------------------------------------
# EKS Managed Node Group Role
# -------------------------------------------------------------------

data "aws_iam_policy_document" "eks_node_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole",
    ]
  }
}


resource "aws_iam_role" "eks_node" {
  name = "${local.name_prefix}-eks-node-role"

  assume_role_policy = (
    data.aws_iam_policy_document.eks_node_assume_role.json
  )

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-eks-node-role"
      Tier = "platform"
    }
  )
}


resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  role = aws_iam_role.eks_node.name

  policy_arn = (
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  )
}


resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  role = aws_iam_role.eks_node.name

  policy_arn = (
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  )
}


resource "aws_iam_role_policy_attachment" "ecr_read_only" {
  role = aws_iam_role.eks_node.name

  policy_arn = (
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  )
}


# -------------------------------------------------------------------
# Platform Worker Role
# -------------------------------------------------------------------

data "aws_iam_policy_document" "worker_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole",
    ]
  }
}


resource "aws_iam_role" "worker" {
  name = "${local.name_prefix}-worker-role"

  assume_role_policy = (
    data.aws_iam_policy_document.worker_assume_role.json
  )

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-worker-role"
      Tier = "worker"
    }
  )
}


data "aws_iam_policy_document" "worker_permissions" {
  statement {
    sid    = "ReadAccountIdentity"
    effect = "Allow"

    actions = [
      "sts:GetCallerIdentity",
    ]

    resources = [
      "*",
    ]
  }

  statement {
    sid    = "DescribeInfrastructure"
    effect = "Allow"

    actions = [
      "ec2:DescribeAvailabilityZones",
      "ec2:DescribeInstances",
      "ec2:DescribeRouteTables",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcs",
    ]

    resources = [
      "*",
    ]
  }
}


resource "aws_iam_policy" "worker" {
  name = "${local.name_prefix}-worker-policy"

  description = (
    "Base permissions for the Platform Launchpad deployment worker."
  )

  policy = data.aws_iam_policy_document.worker_permissions.json

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-worker-policy"
    }
  )
}


resource "aws_iam_role_policy_attachment" "worker" {
  role       = aws_iam_role.worker.name
  policy_arn = aws_iam_policy.worker.arn
}