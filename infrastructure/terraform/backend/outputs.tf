output "ecr_repo_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.backend_repo.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.lx_fta.name
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.ecs_alb.dns_name
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for audit logs"
  value       = aws_dynamodb_table.audit_logs.name
}
