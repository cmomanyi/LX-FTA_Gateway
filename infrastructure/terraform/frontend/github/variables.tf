variable "frontend_bucket_name" {}
variable "custom_domain_name" {}
variable "acm_cert_arn" {}
variable "aws_region" {}
variable "hosted_zone_id" {}
variable "cloudfront_distribution_id" {
  default = ""
}
variable "create_route53_record" {
  default = false
}