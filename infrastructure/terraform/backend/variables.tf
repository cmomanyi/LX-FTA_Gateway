variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "ecr_repo_name" {
  description = "ECR repository name"
  type        = string
  default     = "lx-fta-backend"
}

variable "ecs_cluster_name" {
  description = "ECS cluster name"
  type        = string
  default     = "lx-fta-cluster"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
}

variable "jwt_secret" {
  description = "JWT secret for backend authentication"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID to deploy ECS and ALB"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for ECS tasks and ALB"
  type        = list(string)
}

variable "acm_cert_arn" {
  description = "ARN of ACM certificate for HTTPS"
  type        = string
}