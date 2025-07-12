# Curriculum Builder Infrastructure

## Quick Start

1. **Configure variables:**
   ```bash
   cd environments/sandbox
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your API keys
   ```

2. **Deploy sandbox environment:**
   ```bash
   ./scripts/deploy.sh sandbox us-west-2
   ```

3. **Update secrets with real API keys:**
   ```bash
   aws secretsmanager update-secret \
     --secret-id sandbox-curriculum-secrets \
     --secret-string '{
       "openai_api_key": "your-real-openai-key",
       "anthropic_api_key": "your-real-anthropic-key"
     }'
   ```

## Structure

- `environments/` - Environment-specific configurations
- `modules/` - Reusable Terraform modules
- `shared/` - Common variables and tagging
- `scripts/` - Deployment and management scripts

## Tagging Strategy

All resources are tagged with:
- **System**: curriculum-builder
- **Environment**: sandbox/dev/staging/prod
- **Component**: api/database/vector-store/cache/frontend/sandbox
- **ManagedBy**: terraform
- **Owner**: curriculum-team
- **Project**: curriculum-builder
- **BillingCode**: CURR-001
- **CostCenter**: infrastructure/education

Sandbox resources get additional tags:
- **UserId**: user-abc-123
- **CourseId**: course-xyz-456
- **LessonId**: lesson-def-789
- **TTL**: 2024-12-31T23:59:59Z
- **Purpose**: learning
- **DataClass**: internal

## Next Steps

1. Complete RDS module
2. Complete ElastiCache module
3. Complete ECS cluster module
4. Add monitoring and cost controls
5. Add API Gateway integration