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

resource "aws_ecs_task_definition" "fastapi_task" {
  family                   = var.ecr_repo_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "fastapi"
      image = "${aws_ecr_repository.backend_repo.repository_url}:latest"
      portMappings = [{
        containerPort = 8000,
        hostPort      = 8000
      }]
      environment = [
        { name = "ENV", value = "production" },
        { name = "JWT_SECRET", value = var.jwt_secret }
      ]
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_logs.name,
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_security_group" "ecs_sg" {
  name        = "ecs-sg"
  description = "Allow HTTP for ECS"
  vpc_id      = var.vpc_id

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

resource "aws_lb_listener" "ecs_listener" {
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = 80
  protocol          = "HTTP"

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

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [name]
  }
}