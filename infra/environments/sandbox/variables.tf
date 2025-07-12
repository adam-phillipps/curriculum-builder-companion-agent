variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-west-2"
}

variable "aws_profile" {
  description = "AWS credentials profile name"
  type        = string
  default     = "default"
}

variable "domain_name" {
  description = "Domain name for the application (optional for sandbox)"
  type        = string
  default     = ""
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
  default     = "placeholder-openai-key"
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
  default     = "placeholder-anthropic-key"
}