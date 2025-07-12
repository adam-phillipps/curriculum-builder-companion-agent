output "api_gateway_url" {
  description = "API Gateway invoke URL"
  value       = aws_api_gateway_stage.main.invoke_url
}

output "api_gateway_id" {
  description = "API Gateway REST API ID"
  value       = aws_api_gateway_rest_api.main.id
}

output "custom_domain_url" {
  description = "Custom domain URL (if configured)"
  value       = var.certificate_arn != "" ? "https://${aws_api_gateway_domain_name.main[0].domain_name}" : ""
}