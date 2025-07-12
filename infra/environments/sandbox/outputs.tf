output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.ecs.alb_dns_name
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.elasticache.endpoint
  sensitive   = true
}

output "secrets_arn" {
  description = "Secrets Manager ARN"
  value       = module.secrets.secrets_arn
}

output "frontend_bucket_name" {
  description = "Frontend S3 bucket name"
  value       = module.s3.frontend_bucket_name
}

output "frontend_url" {
  description = "Frontend CloudFront URL"
  value       = module.s3.frontend_cloudfront_url
}

output "ecr_repository_url" {
  description = "ECR repository URL for ngage applications"
  value       = module.ecr.repository_url
}

output "curriculum_api_repository_url" {
  description = "ECR repository URL for curriculum-api"
  value       = module.ecr.curriculum_api_repository_url
}

output "curriculum_migrate_repository_url" {
  description = "ECR repository URL for curriculum-migrate"
  value       = module.ecr.curriculum_migrate_repository_url
}

output "curriculum_docs_repository_url" {
  description = "ECR repository URL for curriculum-docs"
  value       = module.ecr.curriculum_docs_repository_url
}

output "content_bucket_name" {
  description = "Content S3 bucket name"
  value       = module.s3.content_bucket_name
}

output "sandbox_bucket_name" {
  description = "Sandbox S3 bucket name"
  value       = module.s3.sandbox_bucket_name
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.networking.private_subnet_ids
}

output "ecs_security_group_id" {
  description = "ECS security group ID"
  value       = module.networking.ecs_security_group_id
}

output "api_url" {
  description = "API endpoint URL"
  value       = module.api_gateway.custom_domain_url != "" ? module.api_gateway.custom_domain_url : module.api_gateway.api_gateway_url
}

output "api_gateway_url" {
  description = "API Gateway URL"
  value       = module.api_gateway.api_gateway_url
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = module.s3.cloudfront_distribution_id
}