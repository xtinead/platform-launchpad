output "endpoint_security_group_id" {
  description = "Security group used by interface VPC endpoints."
  value       = aws_security_group.endpoints.id
}

output "ecr_api_endpoint_id" {
  description = "ECR API VPC endpoint ID."
  value       = aws_vpc_endpoint.ecr_api.id
}

output "ecr_dkr_endpoint_id" {
  description = "ECR Docker VPC endpoint ID."
  value       = aws_vpc_endpoint.ecr_dkr.id
}

output "ec2_endpoint_id" {
  description = "EC2 VPC endpoint ID."
  value       = aws_vpc_endpoint.ec2.id
}

output "s3_endpoint_id" {
  description = "S3 gateway endpoint ID."
  value       = aws_vpc_endpoint.s3.id
}

output "eks_endpoint_id" {
  description = "Amazon EKS API VPC endpoint ID."
  value       = aws_vpc_endpoint.eks.id
}