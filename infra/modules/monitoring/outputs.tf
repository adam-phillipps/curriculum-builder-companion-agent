/**
 * Outputs for monitoring module
 */

output "api_log_group_name" {
  description = "Name of the API application log group"
  value       = aws_cloudwatch_log_group.api_logs.name
}

output "api_access_log_group_name" {
  description = "Name of the API access log group"
  value       = aws_cloudwatch_log_group.api_access_logs.name
}

output "learning_outcomes_log_group_name" {
  description = "Name of the learning outcomes log group"
  value       = aws_cloudwatch_log_group.learning_outcomes_logs.name
}

output "dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

