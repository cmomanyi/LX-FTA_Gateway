output "website_endpoint" {
  description = "S3 static website endpoint"
  value       = aws_s3_bucket.frontend_bucket.bucket_regional_domain_name
}

output "cloudfront_url" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.frontend_cdn.domain_name
}

output "frontend_bucket" {
  value = aws_s3_bucket.frontend_bucket.id
}

output "ecr_repo_url" {
  value = aws_ecr_repository.backend.repository_url
}