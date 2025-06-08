
output "ecs_service_name" {
  value       = aws_ecs_service.backend_service.name
  description = "The name of the ECS service"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.lx_fta.name
  description = "The name of the ECS cluster"
}

output "alb_dns_name" {
  value       = aws_lb.ecs_alb.dns_name
  description = "Public DNS of the ALB"
}

output "cloudwatch_log_group" {
  value       = aws_cloudwatch_log_group.ecs_logs.name
  description = "CloudWatch log group name"
}
output "dynamodb_audit_table" {
  value       = aws_dynamodb_table.audit_logs.name
  description = "DynamoDB table used for storing audit logs"
}
