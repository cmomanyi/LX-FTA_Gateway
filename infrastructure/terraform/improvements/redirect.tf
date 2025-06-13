provider "aws" {
  region = var.aws_region
}

data "aws_route53_zone" "main" {
  name         = var.domain_name
  private_zone = false
}

# Redirect root domain (lx-gateway.tech) to CloudFront (same as portal.lx-gateway.tech)
resource "aws_route53_record" "root_redirect" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }

  depends_on = [aws_cloudfront_distribution.frontend]

  tags = {
    Name    = "root-domain-redirect"
    Purpose = "Redirect lx-gateway.tech to portal subdomain"
  }
}
