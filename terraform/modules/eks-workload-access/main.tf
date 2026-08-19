locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# -------------------------------------------------------------------
# EKS Workloads -> PostgreSQL
# -------------------------------------------------------------------

resource "aws_vpc_security_group_ingress_rule" "postgres_from_eks" {
  security_group_id = var.postgres_security_group_id

  description = (
    "Allow PostgreSQL access from EKS workloads."
  )

  ip_protocol = "tcp"
  from_port   = var.postgres_port
  to_port     = var.postgres_port

  referenced_security_group_id = (
    var.eks_security_group_id
  )

  tags = local.common_tags
}


# -------------------------------------------------------------------
# EKS Workloads -> Redis
# -------------------------------------------------------------------

resource "aws_vpc_security_group_ingress_rule" "redis_from_eks" {
  security_group_id = var.redis_security_group_id

  description = (
    "Allow Redis access from EKS workloads."
  )

  ip_protocol = "tcp"
  from_port   = var.redis_port
  to_port     = var.redis_port

  referenced_security_group_id = (
    var.eks_security_group_id
  )

  tags = local.common_tags
}