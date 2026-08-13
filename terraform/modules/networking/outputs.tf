output "vpc_id" {
  description = "ID of the Platform Launchpad VPC."
  value       = aws_vpc.this.id
}

output "vpc_arn" {
  description = "ARN of the Platform Launchpad VPC."
  value       = aws_vpc.this.arn
}

output "vpc_cidr" {
  description = "CIDR block assigned to the VPC."
  value       = aws_vpc.this.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets."
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = "IDs of private application subnets."
  value       = aws_subnet.private_app[*].id
}

output "private_db_subnet_ids" {
  description = "IDs of private database subnets."
  value       = aws_subnet.private_db[*].id
}

output "public_route_table_id" {
  description = "ID of the public route table."
  value       = aws_route_table.public.id
}

output "private_app_route_table_id" {
  description = "ID of the private application route table."
  value       = aws_route_table.private_app.id
}

output "private_db_route_table_id" {
  description = "ID of the private database route table."
  value       = aws_route_table.private_db.id
}

output "internet_gateway_id" {
  description = "ID of the VPC Internet Gateway."
  value       = aws_internet_gateway.this.id
}

output "availability_zones" {
  description = "Availability zones used by the networking module."
  value       = var.availability_zones
}