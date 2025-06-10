provider "aws" {
  region = var.aws_region
}

# -------------------------
# FRONTEND: Portal (CloudFront + S3)
# -------------------------
data "aws_s3_bucket" "frontend" {
  bucket = var.frontend_bucket_name
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = data.aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = data.aws_s3_bucket.frontend.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = data.aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Sid       = "PublicReadForWebsite",
      Effect    = "Allow",
      Principal = "*",
      Action    = "s3:GetObject",
      Resource  = "arn:aws:s3:::${data.aws_s3_bucket.frontend.id}/*"
    }]
  })
}

resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  default_root_object = "index.html"
  aliases             = [var.custom_domain_name]

  origin {
    domain_name = "${var.frontend_bucket_name}.s3-website-${var.aws_region}.amazonaws.com"
    origin_id   = "S3WebsiteOrigin"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "S3WebsiteOrigin"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.acm_cert_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

resource "aws_route53_record" "portal_alias" {
  zone_id = var.hosted_zone_id
  name    = var.custom_domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}

# -------------------------
# REDIRECT: www → portal
# -------------------------
resource "aws_s3_bucket" "www_redirect" {
  bucket = "www.lx-gateway.tech"
}

resource "aws_s3_bucket_website_configuration" "www_redirect" {
  bucket = aws_s3_bucket.www_redirect.id

  redirect_all_requests_to {
    host_name = var.custom_domain_name
    protocol  = "https"
  }
}

resource "aws_s3_bucket_public_access_block" "www_redirect" {
  bucket                  = aws_s3_bucket.www_redirect.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "www_redirect" {
  bucket = aws_s3_bucket.www_redirect.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = "*",
      Action    = "s3:GetObject",
      Resource  = "arn:aws:s3:::www.lx-gateway.tech/*"
    }]
  })
}

resource "aws_route53_record" "www_redirect" {
  zone_id = var.hosted_zone_id
  name    = "www.lx-gateway.tech"
  type    = "A"

  alias {
    name                   = "s3-website.${var.aws_region}.amazonaws.com"
    zone_id                = "Z3AQBSTGFYJSTF"  # Global S3 website hosted zone ID
    evaluate_target_health = false
  }
}

# -------------------------
# BACKEND: API domain → ALB
# # -------------------------
# resource "aws_route53_record" "api_backend" {
#   zone_id = var.hosted_zone_id
#   name    = "api.lx-gateway.tech"
#   type    = "A"
#
#   alias {
#     name                   = aws_lb.api_alb.dns_name
#     zone_id                = aws_lb.api_alb.zone_id
#     evaluate_target_health = true
#   }
# }

# Route53 record pointing to ALB
resource "aws_route53_record" "api_alias" {
  zone_id = var.hosted_zone_id
  name    = var.api_domain_name
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = false
  }
}
# Note: You must define your ALB elsewhere like:
# resource "aws_lb" "api_alb" { ... }

