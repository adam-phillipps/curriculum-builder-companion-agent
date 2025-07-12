output "endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
}

output "instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.main.id
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "username" {
  description = "Database username"
  value       = aws_db_instance.main.username
}

output "port" {
  description = "Database port"
  value       = aws_db_instance.main.port
}

output "host" {
  description = "Database host (without port)"
  value       = aws_db_instance.main.address
}