output "eks_cluster_role_name" {
  description = "IAM role name used by the EKS control plane."
  value       = aws_iam_role.eks_cluster.name
}

output "eks_cluster_role_arn" {
  description = "IAM role ARN used by the EKS control plane."
  value       = aws_iam_role.eks_cluster.arn
}

output "eks_node_role_name" {
  description = "IAM role name used by EKS managed nodes."
  value       = aws_iam_role.eks_node.name
}

output "eks_node_role_arn" {
  description = "IAM role ARN used by EKS managed nodes."
  value       = aws_iam_role.eks_node.arn
}

output "worker_role_name" {
  description = "IAM role name used by the Platform Launchpad worker."
  value       = aws_iam_role.worker.name
}

output "worker_role_arn" {
  description = "IAM role ARN used by the Platform Launchpad worker."
  value       = aws_iam_role.worker.arn
}

output "worker_policy_arn" {
  description = "IAM policy ARN attached to the worker role."
  value       = aws_iam_policy.worker.arn
}