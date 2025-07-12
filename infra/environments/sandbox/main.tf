terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  default_tags {
    tags = local.environment_tags
  }
}



locals {
  environment_tags = {
    System      = "curriculum-builder"
    Environment = "sandbox"
    ManagedBy   = "terraform"
    Owner       = "curriculum-team"
    Project     = "curriculum-builder"
    BillingCode = "CURR-001"
    CostCenter  = "infrastructure"
  }
}

# Networking
module "networking" {
  source = "../../modules/networking"
  
  environment = "sandbox"
  tags        = local.environment_tags
}

# Secrets Management
module "secrets" {
  source = "../../modules/secrets"
  
  environment       = "sandbox"
  openai_api_key    = var.openai_api_key
  anthropic_api_key = var.anthropic_api_key
  postgres_host     = module.rds.host
  postgres_db       = "curriculum_builder"
  postgres_user     = "curriculum_user"
  postgres_port     = "5432"
  tags              = local.environment_tags
}

# RDS PostgreSQL
module "rds" {
  source = "../../modules/rds"
  
  environment        = "sandbox"
  vpc_id             = module.networking.vpc_id
  subnet_ids         = module.networking.private_subnet_ids
  security_group_ids = [module.networking.database_security_group_id]
  postgres_password  = module.secrets.postgres_password
  tags               = local.environment_tags
}

# ElastiCache Redis
module "elasticache" {
  source = "../../modules/elasticache"
  
  environment        = "sandbox"
  vpc_id             = module.networking.vpc_id
  subnet_ids         = module.networking.private_subnet_ids
  security_group_ids = [module.networking.cache_security_group_id]
  auth_token         = module.secrets.redis_auth_token
  tags               = local.environment_tags
}

# DNS and SSL (optional - only if domain provided)
module "dns_ssl" {
  source = "../../modules/dns-ssl"
  
  domain_name    = var.domain_name
  api_subdomain  = "api"
  environment    = "sandbox"
  alb_dns_name   = module.ecs.alb_dns_name
  alb_zone_id    = module.ecs.alb_zone_id
  tags           = local.environment_tags
}

# API Gateway for HTTPS
module "api_gateway" {
  source = "../../modules/api-gateway"
  
  environment     = "sandbox"
  alb_dns_name    = module.ecs.alb_dns_name
  domain_name     = var.domain_name
  certificate_arn = module.dns_ssl.certificate_arn
  tags            = local.environment_tags
}

# ECS Cluster
module "ecs" {
  source = "../../modules/ecs-cluster"
  
  environment           = "sandbox"
  vpc_id                = module.networking.vpc_id
  private_subnet_ids    = module.networking.private_subnet_ids
  public_subnet_ids     = module.networking.public_subnet_ids
  alb_security_group_id = module.networking.alb_security_group_id
  ecs_security_group_id = module.networking.ecs_security_group_id
  database_endpoint     = module.rds.endpoint
  redis_endpoint        = module.elasticache.endpoint
  secrets_arn           = module.secrets.secrets_arn
  content_bucket_arn    = module.s3.content_bucket_arn
  sandbox_bucket_arn    = module.s3.sandbox_bucket_arn
  certificate_arn       = module.dns_ssl.certificate_arn
  tags                  = local.environment_tags
}

# ECR Repositories
module "ecr" {
  source = "../../modules/ecr"
  
  environment = "sandbox"
  tags        = local.environment_tags
}

# ECS Services
module "ecs_services" {
  source = "../../modules/ecs-services"
  
  environment             = "sandbox"
  aws_region              = var.aws_region
  task_execution_role_arn = module.ecs.ecs_task_execution_role_arn
  task_role_arn          = module.ecs.ecs_task_role_arn
  database_endpoint       = module.rds.endpoint
  database_host          = module.rds.host
  redis_endpoint          = module.elasticache.endpoint
  secrets_arn            = module.secrets.secrets_arn
  api_log_group          = "/ecs/sandbox-curriculum-api"
  chromadb_log_group     = "/ecs/sandbox-curriculum-chromadb"
  frontend_bucket_name   = module.s3.frontend_bucket_name
  api_image              = "${module.ecr.curriculum_api_repository_url}"
  api_image_tag          = "latest"
  migrate_image          = "${module.ecr.curriculum_migrate_repository_url}"
  migrate_image_tag      = "latest"
  cluster_id             = module.ecs.cluster_arn
  private_subnet_ids     = module.networking.private_subnet_ids
  ecs_security_group_id  = module.networking.ecs_security_group_id
  target_group_arn       = module.ecs.api_target_group_arn
  alb_listener_arn       = ""
  tags                   = local.environment_tags
}

# S3 Storage
module "s3" {
  source = "../../modules/s3"
  
  environment = "sandbox"
  tags        = local.environment_tags
}

