# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.environment}-curriculum-db-subnet-group"
  subnet_ids = var.subnet_ids
  
  tags = merge(var.tags, {
    Name = "${var.environment}-db-subnet-group"
  })
}

# DB Parameter Group
resource "aws_db_parameter_group" "main" {
  family = "postgres15"
  name   = "${var.environment}-curriculum-postgres15"
  
  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }
  
  parameter {
    name  = "log_statement"
    value = "all"
  }
  
  tags = var.tags
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.environment}-curriculum-db"
  
  # Engine
  engine         = "postgres"
  engine_version = "15.8"
  instance_class = var.instance_class
  
  # Storage
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  
  # Database
  db_name  = "curriculum_builder"
  username = "curriculum_user"
  password = var.postgres_password
  
  # Network
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = var.security_group_ids
  publicly_accessible    = false
  
  # Backup
  backup_retention_period = var.backup_retention_days
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  # Monitoring
  performance_insights_enabled = true
  monitoring_interval         = 60
  monitoring_role_arn        = aws_iam_role.rds_monitoring.arn
  
  # Configuration
  parameter_group_name = aws_db_parameter_group.main.name
  
  # Protection
  skip_final_snapshot = var.environment == "sandbox"
  deletion_protection = var.environment == "prod"
  
  tags = merge(var.tags, {
    Name = "${var.environment}-curriculum-db"
  })
}

# IAM Role for RDS Enhanced Monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.environment}-rds-monitoring-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}