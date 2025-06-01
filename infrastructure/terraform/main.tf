# Terraform configuration for LX-FTA Gateway AWS infrastructure

provider "aws" {
  region = "us-east-1"
}

############################
# S3 + CloudFront (Frontend)
############################
resource "aws_s3_bucket" "frontend_bucket" {
  bucket = "lx-fta-frontend"
  acl    = "public-read"
  website {
    index_document = "index.html"
    error_document = "index.html"
  }
}

resource "aws_cloudfront_distribution" "frontend_cdn" {
  origin {
    domain_name = aws_s3_bucket.frontend_bucket.website_endpoint
    origin_id   = "s3-origin"
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-origin"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

##################################
# ECS Cluster + Fargate (Backend)
##################################
resource "aws_ecs_cluster" "lx_fta" {
  name = "lx-fta-cluster"
}

resource "aws_ecs_task_definition" "fastapi_task" {
  family                   = "lx-fta-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "fastapi"
      image = "<YOUR_ECR_IMAGE_URL>"
      portMappings = [{
        containerPort = 8000
        hostPort      = 8000
      }]
      environment = [
        { name = "ENV", value = "production" },
        { name = "JWT_SECRET", value = var.jwt_secret }
      ]
    }
  ])
}

resource "aws_ecs_service" "backend_service" {
  name            = "lx-fta-backend-service"
  cluster         = aws_ecs_cluster.lx_fta.id
  task_definition = aws_ecs_task_definition.fastapi_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.subnet_ids
    security_groups = ["sg-0586e8c4143d76873"]
    assign_public_ip = true
  }
}

########################################
# DynamoDB Table (Logs, Audit, Sensors)
########################################
resource "aws_dynamodb_table" "audit_logs" {
  name         = "lx_fta_audit_logs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "sensor_id"
  range_key    = "timestamp"

  attribute {
    name = "sensor_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }
}

########################################
# IAM Role for ECS Task Execution
########################################
resource "aws_iam_role" "ecs_task_execution" {
  name = "ecsTaskExecutionRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Effect = "Allow",
        Sid    = ""
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_attach" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

############################
# Variables
############################
variable "subnet_ids" {
  type = list(string)
}

variable "jwt_secret" {
  type = string
  sensitive = true
}
