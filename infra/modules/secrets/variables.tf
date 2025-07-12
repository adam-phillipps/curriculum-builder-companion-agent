variable "environment" {
  description = "Environment name"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "postgres_host" {
  description = "PostgreSQL host"
  type        = string
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
  default     = "curriculum_builder"
}

variable "postgres_user" {
  description = "PostgreSQL user"
  type        = string
  default     = "curriculum_user"
}

variable "postgres_port" {
  description = "PostgreSQL port"
  type        = string
  default     = "5432"
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

# Passwords are now generated automatically via random_password resources