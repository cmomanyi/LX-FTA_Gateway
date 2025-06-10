variable "api_domain_name" {}
variable "api_acm_cert_arn" {}
variable "hosted_zone_id" {}
variable "alb_arn" {}                  # Output of aws_lb.ecs_alb.arn
variable "alb_listener_https_port" { default = 443 }
variable "aws_region" {}

variable "target_group_arn" {}