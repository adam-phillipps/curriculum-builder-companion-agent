output "curriculum_api_repository_url" {
  description = "ECR repository URL for curriculum-api"
  value       = aws_ecr_repository.curriculum_api.repository_url
}

output "curriculum_migrate_repository_url" {
  description = "ECR repository URL for curriculum-migrate"
  value       = aws_ecr_repository.curriculum_migrate.repository_url
}

output "curriculum_docs_repository_url" {
  description = "ECR repository URL for curriculum-docs"
  value       = aws_ecr_repository.curriculum_docs.repository_url
}

output "chromadb_mirror_repository_url" {
  description = "ECR repository URL for ChromaDB mirror"
  value       = aws_ecr_repository.chromadb_mirror.repository_url
}

# Backward compatibility
output "repository_url" {
  description = "ECR repository URL for curriculum-api (main)"
  value       = aws_ecr_repository.curriculum_api.repository_url
}