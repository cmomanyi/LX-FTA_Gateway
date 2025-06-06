# variable "aws_region" {
#   description = "AWS region to deploy to"
#   type        = string
#   default     = "us-east-1"
# }

variable "domain_name" {
  description = "Primary domain name"
  type        = string
  default     = "portal.lx-gateway.tech"
}

variable "hosted_zone_name" {
  description = "Route 53 hosted zone domain"
  type        = string
  default     = "lx-gateway.tech"
}

variable "bucket_name" {
  description = "S3 bucket name for frontend hosting"
  type        = string
  default     = "lx-fta-frontend"
}

# variable "vpc_id" {
#   description = "VPC ID to deploy ECS/ALB resources into"
#   type        = string
# }
#
# variable "subnet_ids" {
#   description = "List of subnet IDs for ECS service and Load Balancer"
#   type        = list(string)
# }

# variable "jwt_secret" {
#   description = "JWT Secret for backend API auth"
#   type        = string
# }

variable "cert_arn" {
  description = "ACM Certificate ARN for SSL"
  type        = string
}

variable "hosted_zone_id" {
  description = "The ID of the Route 53 hosted zone"
  type        = string
}
