output "role_arn" {
  description = "AWS Load Balancer Controller Pod Identity IAM role ARN."
  value       = aws_iam_role.controller.arn
}

output "policy_arn" {
  description = "AWS Load Balancer Controller IAM policy ARN."
  value       = aws_iam_policy.controller.arn
}

output "association_id" {
  description = "EKS Pod Identity association ID."
  value = (
    aws_eks_pod_identity_association.controller.association_id
  )
}