locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# -------------------------------------------------------------------
# Endpoint Security Group
# -------------------------------------------------------------------

resource "aws_security_group" "endpoints" {
  name        = "${local.name_prefix}-vpc-endpoints-sg"
  description = "Allow HTTPS access to AWS VPC interface endpoints."
  vpc_id      = var.vpc_id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-vpc-endpoints-sg"
      Tier = "platform"
    }
  )
}


resource "aws_vpc_security_group_ingress_rule" "https_from_vpc" {
  security_group_id = aws_security_group.endpoints.id

  description = "Allow HTTPS access from resources inside the VPC."

  ip_protocol = "tcp"
  from_port   = 443
  to_port     = 443

  cidr_ipv4 = var.vpc_cidr
}


# -------------------------------------------------------------------
# ECR API
# -------------------------------------------------------------------

resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id = var.vpc_id

  service_name = (
    "com.amazonaws.${var.aws_region}.ecr.api"
  )

  vpc_endpoint_type = "Interface"

  subnet_ids = var.private_subnet_ids

  security_group_ids = [
    aws_security_group.endpoints.id,
  ]

  private_dns_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ecr-api-endpoint"
    }
  )
}


# -------------------------------------------------------------------
# ECR Docker Registry
# -------------------------------------------------------------------

resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id = var.vpc_id

  service_name = (
    "com.amazonaws.${var.aws_region}.ecr.dkr"
  )

  vpc_endpoint_type = "Interface"

  subnet_ids = var.private_subnet_ids

  security_group_ids = [
    aws_security_group.endpoints.id,
  ]

  private_dns_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ecr-dkr-endpoint"
    }
  )
}


# -------------------------------------------------------------------
# EC2 API
# -------------------------------------------------------------------

resource "aws_vpc_endpoint" "ec2" {
  vpc_id = var.vpc_id

  service_name = (
    "com.amazonaws.${var.aws_region}.ec2"
  )

  vpc_endpoint_type = "Interface"

  subnet_ids = var.private_subnet_ids

  security_group_ids = [
    aws_security_group.endpoints.id,
  ]

  private_dns_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ec2-endpoint"
    }
  )
}

# -------------------------------------------------------------------
# Amazon EKS API
# -------------------------------------------------------------------

resource "aws_vpc_endpoint" "eks" {
  vpc_id = var.vpc_id

  service_name = (
    "com.amazonaws.${var.aws_region}.eks"
  )

  vpc_endpoint_type = "Interface"

  subnet_ids = var.private_subnet_ids

  security_group_ids = [
    aws_security_group.endpoints.id,
  ]

  private_dns_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-eks-endpoint"
    }
  )
}

# -------------------------------------------------------------------
# S3 Gateway Endpoint
# -------------------------------------------------------------------

resource "aws_vpc_endpoint" "s3" {
  vpc_id = var.vpc_id

  service_name = (
    "com.amazonaws.${var.aws_region}.s3"
  )

  vpc_endpoint_type = "Gateway"

  route_table_ids = [
    var.private_route_table_id,
  ]

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-s3-endpoint"
    }
  )
}

# -------------------------------------------------------------------
# Amazon EKS Auth API
# -------------------------------------------------------------------

resource "aws_vpc_endpoint" "eks_auth" {
  vpc_id = var.vpc_id

  service_name = (
    "com.amazonaws.${var.aws_region}.eks-auth"
  )

  vpc_endpoint_type = "Interface"

  subnet_ids = var.private_subnet_ids

  security_group_ids = [
    aws_security_group.endpoints.id,
  ]

  private_dns_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-eks-auth-endpoint"
    }
  )
}

# -------------------------------------------------------------------
# Elastic Load Balancing API
# -------------------------------------------------------------------

resource "aws_vpc_endpoint" "elasticloadbalancing" {
  vpc_id = var.vpc_id

  service_name = (
    "com.amazonaws.${var.aws_region}.elasticloadbalancing"
  )

  vpc_endpoint_type = "Interface"

  subnet_ids = var.private_subnet_ids

  security_group_ids = [
    aws_security_group.endpoints.id,
  ]

  private_dns_enabled = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-elasticloadbalancing-endpoint"
    }
  )
}