output "api_task_definition_arn" {
  description = "FastAPI task definition ARN"
  value       = aws_ecs_task_definition.api.arn
}

output "chromadb_task_definition_arn" {
  description = "ChromaDB task definition ARN"
  value       = aws_ecs_task_definition.chromadb.arn
}

output "db_migrate_task_definition_arn" {
  description = "Database migration task definition ARN"
  value       = aws_ecs_task_definition.db_migrate.arn
}

output "docs_build_task_definition_arn" {
  description = "Documentation build task definition ARN"
  value       = aws_ecs_task_definition.docs_build.arn
}