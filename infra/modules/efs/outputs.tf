output "file_system_id" {
  description = "EFS file system ID"
  value       = aws_efs_file_system.chromadb.id
}

output "file_system_dns_name" {
  description = "EFS file system DNS name"
  value       = aws_efs_file_system.chromadb.dns_name
}