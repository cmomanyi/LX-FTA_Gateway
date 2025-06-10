provider "aws" {
  region = var.aws_region
}



# Route53 A Record for ALB with alias
resource "aws_route53_record" "api_alias" {
  zone_id = var.hosted_zone_id
  name    = var.api_domain_name
  type    = "A"

  alias {
    name                   = data.aws_lb.api_alb.dns_name
    zone_id                = data.aws_lb.api_alb.zone_id
    evaluate_target_health = true
  }
}

# HTTPS Listener for the ALB
resource "aws_lb_listener" "https" {
  load_balancer_arn = var.alb_arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.api_acm_cert_arn

  default_action {
    type             = "forward"
    target_group_arn = var.target_group_arn
  }
}

# (Optional) Data source to retrieve existing ALB details
data "aws_lb" "api_alb" {
  arn = var.alb_arn
}
