locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# -------------------------------------------------------------------
# Application Load Balancer
# -------------------------------------------------------------------

resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Security group for the public application load balancer."
  vpc_id      = var.vpc_id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-alb-sg"
      Tier = "edge"
    }
  )
}


resource "aws_vpc_security_group_ingress_rule" "alb_http" {
  security_group_id = aws_security_group.alb.id

  description = "Allow public HTTP traffic."

  ip_protocol = "tcp"
  from_port   = 80
  to_port     = 80

  cidr_ipv4 = "0.0.0.0/0"
}


resource "aws_vpc_security_group_ingress_rule" "alb_https" {
  security_group_id = aws_security_group.alb.id

  description = "Allow public HTTPS traffic."

  ip_protocol = "tcp"
  from_port   = 443
  to_port     = 443

  cidr_ipv4 = "0.0.0.0/0"
}


resource "aws_vpc_security_group_egress_rule" "alb_to_application" {
  security_group_id = aws_security_group.alb.id

  description = "Allow ALB traffic to application workloads."

  ip_protocol = "tcp"
  from_port   = var.application_port
  to_port     = var.application_port

  referenced_security_group_id = (
    aws_security_group.application.id
  )
}


# -------------------------------------------------------------------
# Application / Worker Workloads
# -------------------------------------------------------------------

resource "aws_security_group" "application" {
  name = "${local.name_prefix}-application-sg"

  description = (
    "Security group for Platform Launchpad application workloads."
  )

  vpc_id = var.vpc_id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-application-sg"
      Tier = "application"
    }
  )
}


resource "aws_vpc_security_group_ingress_rule" "application_from_alb" {
  security_group_id = aws_security_group.application.id

  description = "Allow application traffic from the ALB."

  ip_protocol = "tcp"
  from_port   = var.application_port
  to_port     = var.application_port

  referenced_security_group_id = aws_security_group.alb.id
}


resource "aws_vpc_security_group_egress_rule" "application_https" {
  security_group_id = aws_security_group.application.id

  description = (
    "Allow HTTPS outbound traffic for AWS APIs and external services."
  )

  ip_protocol = "tcp"
  from_port   = 443
  to_port     = 443

  cidr_ipv4 = "0.0.0.0/0"
}


resource "aws_vpc_security_group_egress_rule" "application_postgres" {
  security_group_id = aws_security_group.application.id

  description = "Allow application access to PostgreSQL."

  ip_protocol = "tcp"
  from_port   = var.postgres_port
  to_port     = var.postgres_port

  referenced_security_group_id = aws_security_group.postgres.id
}


resource "aws_vpc_security_group_egress_rule" "application_redis" {
  security_group_id = aws_security_group.application.id

  description = "Allow application access to Redis."

  ip_protocol = "tcp"
  from_port   = var.redis_port
  to_port     = var.redis_port

  referenced_security_group_id = aws_security_group.redis.id
}


# -------------------------------------------------------------------
# PostgreSQL
# -------------------------------------------------------------------

resource "aws_security_group" "postgres" {
  name = "${local.name_prefix}-postgres-sg"

  description = (
    "Security group for private PostgreSQL database resources."
  )

  vpc_id = var.vpc_id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-postgres-sg"
      Tier = "database"
    }
  )
}


resource "aws_vpc_security_group_ingress_rule" "postgres_from_application" {
  security_group_id = aws_security_group.postgres.id

  description = (
    "Allow PostgreSQL only from application workloads."
  )

  ip_protocol = "tcp"
  from_port   = var.postgres_port
  to_port     = var.postgres_port

  referenced_security_group_id = (
    aws_security_group.application.id
  )
}


# -------------------------------------------------------------------
# Redis
# -------------------------------------------------------------------

resource "aws_security_group" "redis" {
  name        = "${local.name_prefix}-redis-sg"
  description = "Security group for private Redis resources."
  vpc_id      = var.vpc_id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-redis-sg"
      Tier = "cache"
    }
  )
}


resource "aws_vpc_security_group_ingress_rule" "redis_from_application" {
  security_group_id = aws_security_group.redis.id

  description = "Allow Redis only from application workloads."

  ip_protocol = "tcp"
  from_port   = var.redis_port
  to_port     = var.redis_port

  referenced_security_group_id = (
    aws_security_group.application.id
  )
}