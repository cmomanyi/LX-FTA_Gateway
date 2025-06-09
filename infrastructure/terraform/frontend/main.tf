resource "aws_cloudfront_origin_access_control" "frontend_oac" {
  count = var.create_origin_access_control ? 1 : 0

  name                              = "frontend-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
  description                       = "Origin access control for frontend"
}

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

# Example IAM policy documents

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
    actions   = ["s3:*"]
    resources = [
      "arn:aws:s3:::lx-fta-frontend-gdwib5",
      "arn:aws:s3:::lx-fta-frontend-gdwib5/*"
    ]
    effect = "Allow"
  }
}
