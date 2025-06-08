
resource "aws_iam_policy" "frontend_s3_access" {
  name        = "FrontendS3AccessPolicy"
  description = "Policy to allow GitHubActionsDeployRole to access S3 bucket for frontend"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid      = "AllowListBucket",
        Effect   = "Allow",
        Action   = ["s3:ListBucket"],
        Resource = "arn:aws:s3:::${var.bucket_name}"
      },
      {
        Sid      = "AllowPutDeleteObjects",
        Effect   = "Allow",
        Action   = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:DeleteObject"
        ],
        Resource = "arn:aws:s3:::${var.bucket_name}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "frontend_s3_policy_attach" {
  role       = aws_iam_role.github_actions_deploy.name
  policy_arn = aws_iam_policy.frontend_s3_access.arn
}
