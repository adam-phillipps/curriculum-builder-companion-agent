/**
 * EFS (Elastic File System) for persistent storage
 */

# EFS File System for ChromaDB data persistence
resource "aws_efs_file_system" "chromadb" {
  creation_token = "${var.environment}-chromadb-data"
  
  performance_mode = "generalPurpose"
  throughput_mode  = "provisioned"
  provisioned_throughput_in_mibps = 10
  
  encrypted = true
  
  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }
  
  tags = merge(var.tags, {
    Name = "${var.environment}-chromadb-efs"
  })
}

# EFS Mount Targets (one per AZ)
resource "aws_efs_mount_target" "chromadb" {
  count           = length(var.private_subnet_ids)
  file_system_id  = aws_efs_file_system.chromadb.id
  subnet_id       = var.private_subnet_ids[count.index]
  security_groups = [aws_security_group.efs.id]
}

# Security Group for EFS
resource "aws_security_group" "efs" {
  name_prefix = "${var.environment}-efs-"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.tags, {
    Name = "${var.environment}-efs-sg"
  })
}