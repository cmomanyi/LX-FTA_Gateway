variable "frontend_bucket_name" {
  type = string
}

variable "custom_domain_name" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "acm_cert_arn" {
  type = string
}

variable "hosted_zone_id" {
  type = string
}

variable "cloudfront_distribution_id" {
  description = "Use existing CloudFront distribution if provided"
  type        = string
  default     = ""
}

variable "create_route53_record" {
  description = "Whether to create the Route 53 alias record"
  type        = bool
  default     = true
}
