# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.environment}-curriculum-cache-subnet-group"
  subnet_ids = var.subnet_ids
  
  tags = var.tags
}

# ElastiCache Parameter Group
resource "aws_elasticache_parameter_group" "main" {
  family = "redis7"
  name   = "${var.environment}-curriculum-redis7"
  
  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }
  
  tags = var.tags
}

# ElastiCache Replication Group
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.environment}-curriculum-redis"
  description                = "Redis cluster for curriculum builder"
  
  # Configuration
  node_type                  = var.node_type
  port                       = 6379
  parameter_group_name       = aws_elasticache_parameter_group.main.name
  
  # Cluster settings
  num_cache_clusters         = var.num_cache_nodes
  
  # Network
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = var.security_group_ids
  
  # Security
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.auth_token
  
  # Backup
  snapshot_retention_limit   = var.snapshot_retention_limit
  snapshot_window           = "03:00-05:00"
  
  # Maintenance
  maintenance_window        = "sun:05:00-sun:07:00"
  
  # Logging
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_slow.name
    destination_type = "cloudwatch-logs"
    log_format       = "text"
    log_type         = "slow-log"
  }
  
  tags = merge(var.tags, {
    Name = "${var.environment}-curriculum-redis"
  })
}

# CloudWatch Log Group for Redis logs
resource "aws_cloudwatch_log_group" "redis_slow" {
  name              = "/aws/elasticache/${var.environment}-curriculum-redis/slow-log"
  retention_in_days = 7
  
  tags = var.tags
}