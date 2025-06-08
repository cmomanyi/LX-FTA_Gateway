variable "aws_region" {
  default     = "us-east-1"
  description = "AWS region"
}

variable "bucket_name" {
  description = "S3 bucket name"
}

variable "domain_name" {
  description = "Custom domain name like portal.lx-gateway.tech"
}

variable "acm_cert_arn" {
  description = "SSL certificate ARN for the domain"
}
