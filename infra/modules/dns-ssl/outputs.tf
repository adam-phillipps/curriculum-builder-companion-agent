output "certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = var.domain_name != "" ? aws_acm_certificate_validation.main[0].certificate_arn : ""
}

output "api_domain" {
  description = "API domain name"
  value       = var.domain_name != "" ? "${var.api_subdomain}.${var.domain_name}" : ""
}

output "zone_id" {
  description = "Route53 zone ID"
  value       = var.domain_name != "" ? data.aws_route53_zone.main[0].zone_id : ""
}