locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}


# -------------------------------------------------------------------
# VPC
# -------------------------------------------------------------------

resource "aws_vpc" "this" {
  cidr_block = var.vpc_cidr

  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-vpc"
    }
  )
}


# -------------------------------------------------------------------
# Internet Gateway
# -------------------------------------------------------------------

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-igw"
    }
  )
}


# -------------------------------------------------------------------
# Public Subnets
# -------------------------------------------------------------------

resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id = aws_vpc.this.id

  cidr_block = var.public_subnet_cidrs[count.index]

  availability_zone = (
    var.availability_zones[count.index]
  )

  map_public_ip_on_launch = true

  tags = merge(
    local.common_tags,
    {
      Name = (
        "${local.name_prefix}-public-${count.index + 1}"
      )

      Tier = "public"

      "kubernetes.io/role/elb" = "1"
    }
  )
}


# -------------------------------------------------------------------
# Private Application Subnets
# -------------------------------------------------------------------

resource "aws_subnet" "private_app" {
  count = length(var.private_app_subnet_cidrs)

  vpc_id = aws_vpc.this.id

  cidr_block = (
    var.private_app_subnet_cidrs[count.index]
  )

  availability_zone = (
    var.availability_zones[count.index]
  )

  map_public_ip_on_launch = false

  tags = merge(
    local.common_tags,
    {
      Name = (
        "${local.name_prefix}-private-app-${count.index + 1}"
      )

      Tier = "private-app"

      "kubernetes.io/role/internal-elb" = "1"
    }
  )
}


# -------------------------------------------------------------------
# Private Database Subnets
# -------------------------------------------------------------------

resource "aws_subnet" "private_db" {
  count = length(var.private_db_subnet_cidrs)

  vpc_id = aws_vpc.this.id

  cidr_block = (
    var.private_db_subnet_cidrs[count.index]
  )

  availability_zone = (
    var.availability_zones[count.index]
  )

  map_public_ip_on_launch = false

  tags = merge(
    local.common_tags,
    {
      Name = (
        "${local.name_prefix}-private-db-${count.index + 1}"
      )

      Tier = "private-db"
    }
  )
}


# -------------------------------------------------------------------
# Public Route Table
# -------------------------------------------------------------------

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-public-rt"
    }
  )
}


resource "aws_route" "public_internet" {
  route_table_id = aws_route_table.public.id

  destination_cidr_block = "0.0.0.0/0"

  gateway_id = aws_internet_gateway.this.id
}


resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id = aws_subnet.public[count.index].id

  route_table_id = aws_route_table.public.id
}

# -------------------------------------------------------------------
# NAT Gateway
# -------------------------------------------------------------------

resource "aws_eip" "nat" {
  domain = "vpc"

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-nat-eip"
      Tier = "public"
    }
  )
}


resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.nat.id

  subnet_id = aws_subnet.public[0].id

  depends_on = [
    aws_internet_gateway.this,
  ]

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-nat"
      Tier = "public"
    }
  )
}

# -------------------------------------------------------------------
# Private Application Route Table
# -------------------------------------------------------------------

resource "aws_route_table" "private_app" {
  vpc_id = aws_vpc.this.id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-private-app-rt"
    }
  )
}


resource "aws_route_table_association" "private_app" {
  count = length(aws_subnet.private_app)

  subnet_id = aws_subnet.private_app[count.index].id

  route_table_id = aws_route_table.private_app.id
}

resource "aws_route" "private_app_internet" {
  route_table_id = aws_route_table.private_app.id

  destination_cidr_block = "0.0.0.0/0"

  nat_gateway_id = aws_nat_gateway.this.id
}

# -------------------------------------------------------------------
# Private Database Route Table
# -------------------------------------------------------------------

resource "aws_route_table" "private_db" {
  vpc_id = aws_vpc.this.id

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-private-db-rt"
    }
  )
}


resource "aws_route_table_association" "private_db" {
  count = length(aws_subnet.private_db)

  subnet_id = aws_subnet.private_db[count.index].id

  route_table_id = aws_route_table.private_db.id
}