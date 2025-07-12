variable "environment" {
  description = "Environment name (sandbox, dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["sandbox", "dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: sandbox, dev, staging, prod"
  }
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-west-2"
}

variable "multi_region" {
  description = "Enable multi-region deployment"
  type        = bool
  default     = false
}

variable "sandbox_config" {
  description = "Configuration for sandbox resources"
  type = map(object({
    user_id   = string
    course_id = optional(string)
    lesson_id = optional(string)
    ttl       = string
  }))
  default = {}
}

variable "domain_name" {
  description = "Base domain name for the application"
  type        = string
  default     = ""
}

variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_cost_monitoring" {
  description = "Enable cost monitoring and budgets"
  type        = bool
  default     = true
}