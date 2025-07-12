variable "domain_name" {
  description = "Domain name for SSL certificate and DNS records"
  type        = string
  default     = ""
}

variable "api_subdomain" {
  description = "Subdomain for API endpoint (e.g., 'api' for api.domain.com)"
  type        = string
  default     = "api"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "alb_dns_name" {
  description = "ALB DNS name for Route53 alias"
  type        = string
}

variable "alb_zone_id" {
  description = "ALB zone ID for Route53 alias"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}