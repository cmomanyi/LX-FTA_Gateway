provider "aws" {
  region = var.aws_region
}

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

resource "aws_s3_bucket" "frontend" {
  bucket        = "lx-fta-frontend-${random_string.suffix.result}"
  force_destroy = true

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Environment = "Production"
    Project     = "LX-FTA"
  }
}

resource "aws_s3_bucket_website_configuration" "frontend_site" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_cloudfront_origin_access_control" "frontend_oac" {
  name                              = "frontend-oac"
  description                       = "Access for CloudFront to S3"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "frontend_distribution" {
  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "frontend-origin"

    origin_access_control_id = aws_cloudfront_origin_access_control.frontend_oac.id
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "frontend-origin"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.acm_cert_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  tags = {
    Name = "LX-FTA Frontend CDN"
  }
}

resource "aws_iam_role" "github_actions_deploy" {
  name = "GitHubActionsDeployRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com",
          AWS     = "arn:aws:iam::${var.aws_account_id}:root"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [name]
  }
}
resource "aws_iam_role" "github_actions_deploy" {
  name = "GitHubActionsDeployRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Federated = "arn:aws:iam::${var.aws_account_id}:oidc-provider/token.actions.githubusercontent.com"
        },
        Action = "sts:AssumeRoleWithWebIdentity",
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_repo}:ref:refs/heads/main"
          }
        }
      }
    ]
  })
}


resource "aws_iam_policy" "frontend_s3_access" {
  name        = "FrontendS3AccessPolicy"
  description = "Access policy for S3 deployment"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["s3:*"],
        Resource = [
          "arn:aws:s3:::${aws_s3_bucket.frontend.bucket}",
          "arn:aws:s3:::${aws_s3_bucket.frontend.bucket}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "frontend_s3_policy_attach" {
  role       = aws_iam_role.github_actions_deploy.name
  policy_arn = aws_iam_policy.frontend_s3_access.arn
}
