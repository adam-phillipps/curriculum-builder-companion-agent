# Secrets Manager for API keys and sensitive configuration
resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "${var.environment}-curriculum-secrets"
  description = "Application secrets for curriculum builder"
  
  tags = merge(var.tags, {
    Name = "${var.environment}-app-secrets"
  })
}

# Generate secure passwords
resource "random_password" "postgres" {
  length      = 32
  special     = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "random_password" "redis_auth" {
  length  = 32
  special = false
}

resource "random_password" "app_secret" {
  length  = 64
  special = true
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    openai_api_key    = var.openai_api_key
    anthropic_api_key = var.anthropic_api_key
    secret_key        = random_password.app_secret.result
    postgres_password = random_password.postgres.result
    postgres_host     = var.postgres_host
    postgres_db       = var.postgres_db
    postgres_user     = var.postgres_user
    postgres_port     = var.postgres_port
    database_url      = "postgresql+asyncpg://${var.postgres_user}:${random_password.postgres.result}@${var.postgres_host}:${var.postgres_port}/${var.postgres_db}"
    redis_auth_token  = random_password.redis_auth.result
  })
}

# IAM role for ECS tasks to access secrets
resource "aws_iam_role" "ecs_secrets_role" {
  name = "${var.environment}-ecs-secrets-role"
  
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

resource "aws_iam_role_policy" "ecs_secrets_policy" {
  name = "${var.environment}-ecs-secrets-policy"
  role = aws_iam_role.ecs_secrets_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.app_secrets.arn
      }
    ]
  })
}