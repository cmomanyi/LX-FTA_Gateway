
variable "aws_region" {
  type        = string
  description = "The AWS region to deploy resources in"
}

variable "ecr_repo_name" {
  type        = string
  description = "ECR repository name for FastAPI container"
}

variable "ecs_cluster_name" {
  type        = string
  description = "ECS Cluster name"
}

variable "image_tag" {
  type        = string
  description = "Docker image tag to deploy"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID for ECS and ALB resources"
}

variable "subnet_ids" {
  type        = list(string)
  description = "List of subnet IDs for ECS service"
}

variable "acm_cert_arn" {
  type        = string
  description = "ACM certificate ARN for HTTPS listener"
}

variable "auth_secret_name" {
  type        = string
  description = "Name of the secret in Secrets Manager"
}

variable "secretsmanager_secret_arn" {
  type        = string
  description = "Full ARN of the secret in Secrets Manager"
}
variable "audit_log_table_name" {
  type        = string
  default     = "lx_fta_audit_logs"
  description = "Name of the DynamoDB table for audit logs"
}

variable "audit_log_hash_key" {
  type        = string
  default     = "sensor_id"
  description = "Partition key for the audit log table"
}

variable "audit_log_range_key" {
  type        = string
  default     = "timestamp"
  description = "Sort key for the audit log table"
}
variable "jwt_secret" {
  description = "JWT signing secret"
  type        = string
}


variable "alb_arn" {
  description = "ARN of the Application Load Balancer"
  type        = string
}                 # Output of aws_lb.ecs_alb.arn
variable "alb_listener_https_port" { default = 443 }


