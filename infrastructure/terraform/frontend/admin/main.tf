# Fetch the S3 bucket by name
data "aws_s3_bucket" "frontend" {
  bucket = var.frontend_bucket_name
}

# Website configuration for the S3 bucket
resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = data.aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

# Allow public access to S3 website bucket
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = data.aws_s3_bucket.frontend.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Bucket policy to allow public read
resource "aws_s3_bucket_policy" "frontend" {
  bucket = data.aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "PublicReadForWebsite",
        Effect    = "Allow",
        Principal = "*",
        Action    = "s3:GetObject",
        Resource  = "arn:aws:s3:::${data.aws_s3_bucket.frontend.id}/*"
      }
    ]
  })
}

# If importing, fetch existing CloudFront distribution
data "aws_cloudfront_distribution" "imported" {
  count = var.cloudfront_distribution_id != "" ? 1 : 0
  id    = var.cloudfront_distribution_id
}

# Conditionally create CloudFront distribution
resource "aws_cloudfront_distribution" "frontend" {
  count               = var.cloudfront_distribution_id != "" ? 0 : 1
  enabled             = true
  default_root_object = "index.html"

  aliases = [var.custom_domain_name]

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

# Choose the correct domain name for the Route53 alias
locals {
  cloudfront_alias_domain = (
    var.cloudfront_distribution_id != ""
    ? data.aws_cloudfront_distribution.imported[0].domain_name
    : aws_cloudfront_distribution.frontend[0].domain_name
  )
}

# Conditionally create Route53 alias record
resource "aws_route53_record" "frontend_alias" {
  count   = var.create_route53_record ? 1 : 0
  zone_id = var.hosted_zone_id
  name    = var.custom_domain_name
  type    = "A"

  alias {
    name                   = local.cloudfront_alias_domain
    zone_id                = "Z2FDTNDATAQYW2" # CloudFront hosted zone ID
    evaluate_target_health = false
  }
}
