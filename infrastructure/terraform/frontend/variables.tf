provider "aws" {
  region = "us-east-1"
}

variable "cert_arn" {
  default = "arn:aws:acm:us-east-1:263307268672:certificate/3e017cdc-f90a-41be-9c85-72e264d34cd2"
}

variable "domain_name" {
  default = "portal.lx-gateway.tech"
}

variable "hosted_zone_id" {
  default = "Z0357093XHYR1IYCV5T3"
}

# Assume bucket already exists manually (skip creation to avoid conflict)
data "aws_s3_bucket" "frontend" {
  bucket = "lx-fta-frontend"
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
variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "LX-FTA_Gateway"
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
  default     = "263307268672"
}
