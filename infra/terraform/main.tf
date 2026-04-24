provider "aws" {
  region = var.aws_region
}

# -------------------------
# VPC (self-contained)
# -------------------------
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name   = "scraper-news-vpc"
  cidr   = "10.0.0.0/16"

  azs            = ["eu-north-1a", "eu-north-1b"]
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]

  enable_nat_gateway = false
}

# -------------------------
# ECS Cluster
# -------------------------
resource "aws_ecs_cluster" "this" {
  name = var.ecs_cluster_name
}

# -------------------------
# Task Execution Role
# -------------------------
data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

# -------------------------
# CloudWatch Logs
# -------------------------
resource "aws_cloudwatch_log_group" "scraper" {
  name              = "/ecs/scraper-news"
  retention_in_days = 7
}

# -------------------------
# Security Groups
# -------------------------
resource "aws_security_group" "alb" {
  name        = "scraper-news-alb-sg"
  description = "Allow HTTP and HTTPS inbound"
  vpc_id      = module.vpc.vpc_id

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

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs" {
  name        = "scraper-news-ecs-sg"
  description = "Allow ALB to reach ECS tasks"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# -------------------------
# Load Balancer
# -------------------------
resource "aws_lb" "this" {
  name               = "scraper-news-alb"
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets
}

resource "aws_lb_target_group" "this" {
  name        = "tg-scraper-news"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    interval            = 300
    timeout             = 120
    healthy_threshold   = 2
    unhealthy_threshold = 10
  }

}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# -------------------------
# Task Definition
# -------------------------
resource "aws_ecs_task_definition" "this" {
  family                   = "scraper-news-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory

  execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
  task_role_arn      = aws_iam_role.scraper_task_role.arn

  container_definitions = jsonencode([
    {
      name      = var.container_name
      image     = var.image_url
      essential = true

      environment = [
        {
          name  = "APP_ENV"
          value = "uat"
        },
        {
          name  = "HF_TOKEN"
          value = var.hf_token
        }
      ]


      portMappings = [
        {
          containerPort = var.container_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options   = {
          awslogs-group         = aws_cloudwatch_log_group.scraper.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# -------------------------
# IAM role and policy for S3 boto
# -------------------------
resource "aws_iam_role" "scraper_task_role" {
  name = "scraper-task-role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "scraper_task_role_s3" {
  role = aws_iam_role.scraper_task_role.id

  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::scraper-storage-uat",
          "arn:aws:s3:::scraper-storage-uat/*"
        ]
      }
    ]
  })
}


# -------------------------
# ECS Service
# -------------------------
resource "aws_ecs_service" "this" {
  name            = var.ecs_service_name
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.public_subnets
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.this.arn
    container_name   = var.container_name
    container_port   = var.container_port
  }

  health_check_grace_period_seconds = 120

  depends_on = [
    aws_lb_listener.http,
    aws_lb_listener.https
  ]
}

# -------------------------
# Route53 ALIAS
# -------------------------
resource "aws_route53_record" "alb_alias" {
  zone_id = var.hosted_zone_id
  name    = var.domain_prefix
  type    = "A"

  alias {
    name                   = aws_lb.this.dns_name
    zone_id                = aws_lb.this.zone_id
    evaluate_target_health = true
  }
}
