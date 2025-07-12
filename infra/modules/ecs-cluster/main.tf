# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.environment}-curriculum-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = merge(var.tags, {
    Name = "${var.environment}-curriculum-cluster"
  })
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.environment}-curriculum-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids
  
  enable_deletion_protection = var.environment == "prod"
  
  tags = merge(var.tags, {
    Name = "${var.environment}-curriculum-alb"
  })
}

# Target Groups
resource "aws_lb_target_group" "api" {
  name        = "${var.environment}-api-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
  
  tags = var.tags
}



# ALB Listeners - All traffic goes to API since frontend is in S3
resource "aws_lb_listener" "main" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type = "forward"
    forward {
      target_group {
        arn = aws_lb_target_group.api.arn
      }
    }
  }
}

# IAM Roles
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.environment}-ecs-task-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_secrets_access" {
  name = "${var.environment}-ecs-secrets-access"
  role = aws_iam_role.ecs_task_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = var.secrets_arn
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task" {
  name = "${var.environment}-ecs-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = var.tags
}

resource "aws_iam_role_policy" "ecs_task_s3_access" {
  name = "${var.environment}-ecs-task-s3-access"
  role = aws_iam_role.ecs_task.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${var.content_bucket_arn}/*",
          "${var.sandbox_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          var.content_bucket_arn,
          var.sandbox_bucket_arn
        ]
      }
    ]
  })
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.environment}-curriculum-api"
  retention_in_days = 7
  
  tags = var.tags
}



resource "aws_cloudwatch_log_group" "chromadb" {
  name              = "/ecs/${var.environment}-curriculum-chromadb"
  retention_in_days = 7
  
  tags = var.tags
}