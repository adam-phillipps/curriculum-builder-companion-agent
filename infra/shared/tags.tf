locals {
  # Core tags applied to ALL resources
  common_tags = {
    System      = "curriculum-builder"
    ManagedBy   = "terraform"
    Owner       = "curriculum-team"
    Project     = "curriculum-builder"
    BillingCode = "CURR-001"
  }

  # Environment-specific tags (merged with common_tags)
  environment_tags = merge(local.common_tags, {
    Environment = var.environment
    CostCenter  = var.environment == "prod" ? "education" : "infrastructure"
  })

  # Component-specific tag builder
  component_tags = {
    api          = merge(local.environment_tags, { Component = "api" })
    database     = merge(local.environment_tags, { Component = "database" })
    vector_store = merge(local.environment_tags, { Component = "vector-store" })
    cache        = merge(local.environment_tags, { Component = "cache" })
    frontend     = merge(local.environment_tags, { Component = "frontend" })
    sandbox      = merge(local.environment_tags, { Component = "sandbox" })
    monitoring   = merge(local.environment_tags, { Component = "monitoring" })
    networking   = merge(local.environment_tags, { Component = "networking" })
  }

  # Sandbox-specific tags (for user resources)
  sandbox_tags = {
    for k, v in var.sandbox_config : k => merge(local.component_tags.sandbox, {
      UserId    = v.user_id
      CourseId  = lookup(v, "course_id", null)
      LessonId  = lookup(v, "lesson_id", null)
      TTL       = v.ttl
      Purpose   = "learning"
      DataClass = "internal"
    })
  }
}