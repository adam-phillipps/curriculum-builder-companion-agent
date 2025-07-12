terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "curriculum-builder-terraform-state-4503d1b4"
    key            = "secrets-update/terraform.tfstate"
    region         = "us-west-2"
    use_lockfile   = true
    encrypt        = true
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

# Update existing secret with real API keys
resource "aws_secretsmanager_secret_version" "update_keys" {
  secret_id = var.secrets_manager_arn
  secret_string = jsonencode({
    openai_api_key    = var.openai_api_key
    anthropic_api_key = var.anthropic_api_key
    # Preserve existing generated secrets
    secret_key        = var.app_secret_key
    postgres_password = var.postgres_password
    redis_auth_token  = var.redis_auth_token
  })
}