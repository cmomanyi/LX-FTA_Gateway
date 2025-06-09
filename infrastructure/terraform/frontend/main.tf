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

resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  default_root_object = "index.html"

  aliases = [var.domain_name]

  origin {
    domain_name = "${data.aws_s3_bucket.frontend.id}.s3-website-us-east-1.amazonaws.com"
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

    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.cert_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Environment = "Production"
  }
}

resource "aws_route53_record" "frontend_alias" {
  zone_id = var.hosted_zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}

# Optional: OAC if using S3 REST endpoint (disabled for website hosting)
resource "aws_cloudfront_origin_access_control" "frontend_oac" {
  count                             = var.create_origin_access_control ? 1 : 0
  name                              = "frontend-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
  description                       = "Origin access control for frontend"
}

# IAM role for GitHub Actions OIDC
resource "aws_iam_role" "github_actions_deploy" {
  count = var.create_iam_role ? 1 : 0

  name               = "GitHubActionsDeployRole"
  assume_role_policy = data.aws_iam_policy_document.github_oidc_assume_role.json
}

resource "aws_iam_policy" "frontend_s3_access" {
  count       = var.create_iam_policy ? 1 : 0
  name        = "FrontendS3AccessPolicy"
  description = "Allow GitHub Actions to access S3 bucket for frontend"
  policy      = data.aws_iam_policy_document.s3_policy.json
}

resource "aws_iam_role_policy_attachment" "github_attach_policy" {
  count      = var.create_iam_policy && var.create_iam_role ? 1 : 0
  role       = aws_iam_role.github_actions_deploy[0].name
  policy_arn = aws_iam_policy.frontend_s3_access[0].arn
}

data "aws_iam_policy_document" "github_oidc_assume_role" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    principals {
      type        = "Federated"
      identifiers = ["arn:aws:iam::263307268672:oidc-provider/token.actions.githubusercontent.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:cmomanyi/LX-FTA_Gateway:ref:refs/heads/main"]
    }
  }
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions   = ["s3:*", "cloudfront:CreateInvalidation"]
    resources = [
      "arn:aws:s3:::lx-fta-frontend-gdwib5",
      "arn:aws:s3:::lx-fta-frontend-gdwib5/*"
    ]
    effect = "Allow"
  }
}
