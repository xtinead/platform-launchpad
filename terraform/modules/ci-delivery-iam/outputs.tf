output "jenkins_user_name" {
  description = "Jenkins bootstrap IAM user name."
  value       = aws_iam_user.jenkins.name
}

output "jenkins_user_arn" {
  description = "Jenkins bootstrap IAM user ARN."
  value       = aws_iam_user.jenkins.arn
}

output "role_name" {
  description = "CI delivery IAM role name."
  value       = aws_iam_role.ci_delivery.name
}

output "role_arn" {
  description = "CI delivery IAM role ARN."
  value       = aws_iam_role.ci_delivery.arn
}

output "ecr_publish_policy_arn" {
  description = "CI delivery ECR publication policy ARN."
  value       = aws_iam_policy.ecr_publish.arn
}

output "jenkins_assume_role_policy_arn" {
  description = "Policy allowing Jenkins to assume the CI delivery role."
  value       = aws_iam_policy.jenkins_assume_role.arn
}