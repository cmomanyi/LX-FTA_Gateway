
provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "backend_repo" {
  name = var.ecr_repo_name

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [name]
  }
}

resource "aws_ecs_cluster" "lx_fta" {
  name = var.ecs_cluster_name
}

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.ecr_repo_name}"
  retention_in_days = 7
}

resource "aws_iam_role" "ecs_task_execution" {
  name = "ecsTaskExecutionRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Effect = "Allow",
      Sid    = ""
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_attach" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "secrets_access" {
  name = "AllowSecretsManagerAccess"
  role = aws_iam_role.ecs_task_execution.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = ["secretsmanager:GetSecretValue"],
      Resource = var.secretsmanager_secret_arn
    }]
  })
}

resource "aws_ecs_task_definition" "fastapi_task" {
  family                   = var.ecr_repo_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "fastapi",
      image = "${aws_ecr_repository.backend_repo.repository_url}:${var.image_tag}",
      portMappings = [{
        containerPort = 8000,
        hostPort      = 8000
      }],
      command = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
      environment = [
        { name = "ENV", value = "production" },
        { name = "AWS_REGION", value = var.aws_region },
        { name = "AUTH_SECRET_NAME", value = var.auth_secret_name }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_logs.name,
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "ecs"
        }
      },
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        interval    = 30,
        timeout     = 5,
        retries     = 3,
        startPeriod = 10
      }
    }
  ])
}

resource "aws_security_group" "ecs_sg" {
  name        = "ecs-sg"
  description = "Allow HTTP, HTTPS, and FastAPI ports for ECS"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "ecs_alb" {
  name               = "ecs-alb"
  load_balancer_type = "application"
  subnets            = distinct(var.subnet_ids)
  security_groups    = [aws_security_group.ecs_sg.id]
}

resource "aws_lb_target_group" "ecs_tg" {
  name        = "ecs-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path = "/health"
  }
}

resource "aws_lb_listener" "ecs_listener_http" {
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_tg.arn
  }
}

resource "aws_lb_listener" "ecs_listener_https" {
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.acm_cert_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_tg.arn
  }
}

resource "aws_ecs_service" "backend_service" {
  name            = "${var.ecr_repo_name}-service"
  cluster         = aws_ecs_cluster.lx_fta.id
  task_definition = aws_ecs_task_definition.fastapi_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = distinct(var.subnet_ids)
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_tg.arn
    container_name   = "fastapi"
    container_port   = 8000
  }
}
# resource "aws_dynamodb_table" "audit_logs" {
#   name         = "lx_fta_audit_logs"
#   billing_mode = "PAY_PER_REQUEST"
#   hash_key     = "sensor_id"
#   range_key    = "timestamp"
#
#   attribute {
#     name = "sensor_id"
#     type = "S"
#   }
#
#   attribute {
#     name = "timestamp"
#     type = "S"
#   }
#
#   lifecycle {
#     prevent_destroy = true
#     ignore_changes  = [name]
#   }
# }
#
resource "aws_dynamodb_table" "audit_logs" {
  name         = var.audit_log_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = var.audit_log_hash_key
  range_key    = var.audit_log_range_key

  attribute {
    name = var.audit_log_hash_key
    type = "S"
  }

  attribute {
    name = var.audit_log_range_key
    type = "S"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [name]
  }
}
