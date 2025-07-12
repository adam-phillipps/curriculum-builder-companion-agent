output "secrets_arn" {
  description = "ARN of the secrets manager secret"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

output "ecs_secrets_role_arn" {
  description = "ARN of the ECS secrets access role"
  value       = aws_iam_role.ecs_secrets_role.arn
}

output "postgres_password" {
  description = "Generated PostgreSQL password"
  value       = random_password.postgres.result
  sensitive   = true
}

output "redis_auth_token" {
  description = "Generated Redis auth token"
  value       = random_password.redis_auth.result
  sensitive   = true
}