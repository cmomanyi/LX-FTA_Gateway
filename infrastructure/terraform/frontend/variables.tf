
variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "frontend_bucket_name" {
  type        = string
  description = "S3 bucket name for frontend hosting"
  default     = "lx-fta-frontend"
}

variable "acm_cert_arn" {
  type        = string
  description = "ACM Certificate ARN for HTTPS"
  default     = "arn:aws:acm:us-east-1:263307268672:certificate/3e017cdc-f90a-41be-9c85-72e264d34cd2"
}

variable "route53_zone_id" {
  type        = string
  description = "Route 53 Hosted Zone ID for the domain"
  default     = "Z0357093XHYR1IYCV5T3"
}

variable "custom_domain_name" {
  type        = string
  description = "Custom domain name for CloudFront"
  default     = "portal.lx-gateway.tech"
}

variable "aws_account_id" {
  description = "Your AWS Account ID"
  default = "263307268672"
}
variable "github_repo" {
  type        = string
  description = "GitHub repository in format owner/repo"
  default = "cmomanyi/LX-FTA_Gateway"
}
