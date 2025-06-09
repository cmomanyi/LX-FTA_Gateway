variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "frontend_bucket_name" {
  description = "Name of the frontend S3 bucket"
  type        = string
}

variable "custom_domain_name" {
  description = "Custom domain name"
  type        = string
}

variable "acm_cert_arn" {
  description = "ACM Certificate ARN"
  type        = string
}

variable "hosted_zone_id" {
  description = "Route 53 Hosted Zone ID"
  type        = string
}
