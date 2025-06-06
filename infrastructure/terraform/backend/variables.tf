variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "ecr_repo_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "lx-fta-backend"
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
  default     = "lx-fta-cluster"
}

variable "jwt_secret" {
  description = "JWT secret for FastAPI backend"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for ECS and ALB resources"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for ECS tasks and ALB"
  type        = list(string)
}
