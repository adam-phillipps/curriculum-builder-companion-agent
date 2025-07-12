variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "aws_profile" {
  description = "AWS credentials profile name"
  type        = string
  default     = "default"
}

variable "secrets_manager_arn" {
  description = "ARN of the Secrets Manager secret to update"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
}

variable "app_secret_key" {
  description = "Application secret key (from main deployment)"
  type        = string
  sensitive   = true
}

variable "postgres_password" {
  description = "PostgreSQL password (from main deployment)"
  type        = string
  sensitive   = true
}

variable "redis_auth_token" {
  description = "Redis auth token (from main deployment)"
  type        = string
  sensitive   = true
}