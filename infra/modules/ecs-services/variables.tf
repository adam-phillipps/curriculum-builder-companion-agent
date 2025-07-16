variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# Task execution and role ARNs
variable "task_execution_role_arn" {
  description = "ECS task execution role ARN"
  type        = string
}

variable "task_role_arn" {
  description = "ECS task role ARN"
  type        = string
}

# Infrastructure endpoints
variable "database_endpoint" {
  description = "RDS database endpoint"
  type        = string
}

variable "database_host" {
  description = "RDS database host (without port)"
  type        = string
}

variable "redis_endpoint" {
  description = "Redis endpoint"
  type        = string
}

variable "secrets_arn" {
  description = "Secrets Manager ARN"
  type        = string
}

# Log groups
variable "api_log_group" {
  description = "API CloudWatch log group name"
  type        = string
}

variable "chromadb_log_group" {
  description = "ChromaDB CloudWatch log group name"
  type        = string
}

# API service configuration
variable "api_image" {
  description = "FastAPI container image"
  type        = string
  default     = "curriculum-builder-api"
}

variable "api_image_tag" {
  description = "FastAPI container image tag"
  type        = string
  default     = "latest"
}

variable "migrate_image" {
  description = "Migration Docker image URL"
  type        = string
}

variable "migrate_image_tag" {
  description = "Migration Docker image tag"
  type        = string
  default     = "latest"
}

variable "api_cpu" {
  description = "CPU units for API service"
  type        = number
  default     = 512
}

variable "api_memory" {
  description = "Memory for API service"
  type        = number
  default     = 1024
}

# ChromaDB service configuration
variable "chromadb_image" {
  description = "ChromaDB container image"
  type        = string
  default     = "chromadb/chroma"
}

variable "chromadb_image_tag" {
  description = "ChromaDB container image tag"
  type        = string
  default     = "latest"
}

variable "chromadb_cpu" {
  description = "CPU units for ChromaDB service"
  type        = number
  default     = 256
}

variable "chromadb_memory" {
  description = "Memory for ChromaDB service"
  type        = number
  default     = 512
}

variable "chromadb_port" {
  description = "ChromaDB service port"
  type        = number
  default     = 8000
}

variable "frontend_bucket_name" {
  description = "Frontend S3 bucket name for documentation deployment"
  type        = string
}

variable "cluster_id" {
  description = "ECS cluster ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS services"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "ECS security group ID"
  type        = string
}

variable "target_group_arn" {
  description = "ALB target group ARN"
  type        = string
}

variable "alb_listener_arn" {
  description = "ALB listener ARN"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for service discovery"
  type        = string
}

variable "efs_file_system_id" {
  description = "EFS file system ID for ChromaDB persistence"
  type        = string
  default     = ""
}