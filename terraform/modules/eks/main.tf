locals {
  name_prefix  = "${var.project_name}-${var.environment}"
  cluster_name = "${local.name_prefix}-eks"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# -------------------------------------------------------------------
# EKS Control Plane
# -------------------------------------------------------------------

resource "aws_eks_cluster" "this" {
  name     = local.cluster_name
  role_arn = var.cluster_role_arn
  version  = var.kubernetes_version

  bootstrap_self_managed_addons = false

  enabled_cluster_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler",
  ]

  access_config {
    authentication_mode                         = "API"
    bootstrap_cluster_creator_admin_permissions = false
  }

  upgrade_policy {
    support_type = "STANDARD"
  }

  vpc_config {
    subnet_ids = var.private_subnet_ids

    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.public_access_cidrs
  }

  tags = merge(
    local.common_tags,
    {
      Name = local.cluster_name
      Tier = "platform"
    }
  )
}


# -------------------------------------------------------------------
# Cluster Administrator Access
# -------------------------------------------------------------------

resource "aws_eks_access_entry" "admin" {
  cluster_name  = aws_eks_cluster.this.name
  principal_arn = var.admin_principal_arn
  type          = "STANDARD"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-cluster-admin-access"
    }
  )
}


resource "aws_eks_access_policy_association" "admin" {
  cluster_name  = aws_eks_cluster.this.name
  principal_arn = aws_eks_access_entry.admin.principal_arn

  policy_arn = (
    "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  )

  access_scope {
    type = "cluster"
  }
}


# -------------------------------------------------------------------
# Amazon VPC CNI Managed Add-on
# -------------------------------------------------------------------

resource "aws_eks_addon" "vpc_cni" {
  cluster_name = aws_eks_cluster.this.name
  addon_name   = "vpc-cni"

  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "PRESERVE"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-vpc-cni"
      Tier = "platform"
    }
  )
}


# -------------------------------------------------------------------
# Managed Node Group
# -------------------------------------------------------------------

resource "aws_eks_node_group" "primary" {
  cluster_name = aws_eks_cluster.this.name

  node_group_name = (
    "${local.name_prefix}-primary"
  )

  node_role_arn = var.node_role_arn
  subnet_ids    = var.private_subnet_ids

  instance_types = var.node_instance_types
  capacity_type  = var.node_capacity_type

  ami_type  = "AL2023_x86_64_STANDARD"
  disk_size = var.node_disk_size

  version = var.kubernetes_version

  scaling_config {
    desired_size = var.node_desired_size
    min_size     = var.node_min_size
    max_size     = var.node_max_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    workload = "platform"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-primary-node-group"
      Tier = "platform"
    }
  )

  depends_on = [
    aws_eks_access_policy_association.admin,
    aws_eks_addon.vpc_cni,
  ]
}


# -------------------------------------------------------------------
# kube-proxy Managed Add-on
# -------------------------------------------------------------------

resource "aws_eks_addon" "kube_proxy" {
  cluster_name = aws_eks_cluster.this.name
  addon_name   = "kube-proxy"

  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "PRESERVE"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-kube-proxy"
      Tier = "platform"
    }
  )

  depends_on = [
    aws_eks_node_group.primary,
  ]
}


# -------------------------------------------------------------------
# CoreDNS Managed Add-on
# -------------------------------------------------------------------

resource "aws_eks_addon" "coredns" {
  cluster_name = aws_eks_cluster.this.name
  addon_name   = "coredns"

  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "PRESERVE"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-coredns"
      Tier = "platform"
    }
  )

  depends_on = [
    aws_eks_node_group.primary,
    aws_eks_addon.vpc_cni,
  ]
}

# -------------------------------------------------------------------
# EKS Pod Identity Agent Managed Add-on
# -------------------------------------------------------------------

resource "aws_eks_addon" "pod_identity_agent" {
  cluster_name = aws_eks_cluster.this.name
  addon_name   = "eks-pod-identity-agent"

  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "PRESERVE"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-pod-identity-agent"
      Tier = "platform"
    }
  )

  depends_on = [
    aws_eks_node_group.primary,
  ]
}