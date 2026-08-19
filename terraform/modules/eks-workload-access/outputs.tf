output "postgres_ingress_rule_id" {
  description = "Ingress rule allowing EKS workloads to reach PostgreSQL."
  value = (
    aws_vpc_security_group_ingress_rule.postgres_from_eks.id
  )
}

output "redis_ingress_rule_id" {
  description = "Ingress rule allowing EKS workloads to reach Redis."
  value = (
    aws_vpc_security_group_ingress_rule.redis_from_eks.id
  )
}