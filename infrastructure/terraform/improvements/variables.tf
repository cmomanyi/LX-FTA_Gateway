variable "hosted_zone_id" {}
variable "acm_cert_arn" {}
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