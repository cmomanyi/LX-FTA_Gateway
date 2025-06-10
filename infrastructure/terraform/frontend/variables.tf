variable "frontend_bucket_name" {}
variable "custom_domain_name" {
}
variable "hosted_zone_id" {}
variable "acm_cert_arn" {}
variable "aws_region" {}

variable "alb_dns_name" {}
variable "alb_zone_id" {}
variable "api_domain_name" { default = "api.lx-gateway.tech" }
# Create HTTPS Listener for ALB
variable "target_group_arn" {
  default = ""
}
variable "alb_arn" {
  default = ""
}
variable "api_alb_dns_name" {
  description = "DNS name of the Application Load Balancer (e.g., from aws_lb.api_alb.dns_name)"
  type        = string
}

variable "api_alb_zone_id" {
  description = "Hosted zone ID of the ALB (e.g., from aws_lb.api_alb.zone_id)"
  type        = string
}