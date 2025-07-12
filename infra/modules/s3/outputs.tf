output "frontend_bucket_name" {
  description = "Frontend assets bucket name"
  value       = aws_s3_bucket.frontend.bucket
}

output "frontend_cloudfront_url" {
  description = "Frontend CloudFront distribution URL"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "frontend_bucket_website_endpoint" {
  description = "Frontend bucket website endpoint"
  value       = aws_s3_bucket_website_configuration.frontend.website_endpoint
}

output "content_bucket_name" {
  description = "Learning content bucket name"
  value       = aws_s3_bucket.content.bucket
}

output "sandbox_bucket_name" {
  description = "Sandbox artifacts bucket name"
  value       = aws_s3_bucket.sandbox.bucket
}

output "content_bucket_arn" {
  description = "Learning content bucket ARN"
  value       = aws_s3_bucket.content.arn
}

output "sandbox_bucket_arn" {
  description = "Sandbox artifacts bucket ARN"
  value       = aws_s3_bucket.sandbox.arn
}

output "frontend_bucket_arn" {
  description = "Frontend assets bucket ARN"
  value       = aws_s3_bucket.frontend.arn
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.frontend.id
}