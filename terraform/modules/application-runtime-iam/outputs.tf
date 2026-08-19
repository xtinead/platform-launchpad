output "role_arn" {
  description = "Application runtime Pod Identity IAM role ARN."
  value       = aws_iam_role.runtime.arn
}

output "policy_arn" {
  description = "Application runtime Secrets Manager policy ARN."
  value       = aws_iam_policy.runtime_secrets.arn
}

output "pod_identity_association_ids" {
  description = "Pod Identity association IDs by service account."
  value = {
    for name, association in aws_eks_pod_identity_association.runtime :
    name => association.association_id
  }
}