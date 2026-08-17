output "cluster_name" {
  description = "Name of the EKS cluster."
  value       = aws_eks_cluster.this.name
}

output "cluster_arn" {
  description = "ARN of the EKS cluster."
  value       = aws_eks_cluster.this.arn
}

output "cluster_endpoint" {
  description = "Kubernetes API endpoint for the EKS cluster."
  value       = aws_eks_cluster.this.endpoint
}

output "cluster_version" {
  description = "Kubernetes version used by the EKS cluster."
  value       = aws_eks_cluster.this.version
}

output "cluster_security_group_id" {
  description = "Security group created by EKS for the cluster."
  value       = aws_eks_cluster.this.vpc_config[0].cluster_security_group_id
}

output "cluster_certificate_authority_data" {
  description = "Base64-encoded Kubernetes cluster certificate authority data."
  value       = aws_eks_cluster.this.certificate_authority[0].data
  sensitive   = true
}

output "node_group_name" {
  description = "Name of the primary managed node group."
  value       = aws_eks_node_group.primary.node_group_name
}

output "node_group_arn" {
  description = "ARN of the primary managed node group."
  value       = aws_eks_node_group.primary.arn
}

output "node_group_status" {
  description = "Current status of the primary managed node group."
  value       = aws_eks_node_group.primary.status
}