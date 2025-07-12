#!/bin/bash
set -e

ENVIRONMENT=${1:-sandbox}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECRETS_DIR="$SCRIPT_DIR/../secrets-update"
MAIN_DIR="$SCRIPT_DIR/../environments/$ENVIRONMENT"

# Parse command line arguments
OPENAI_KEY=""
ANTHROPIC_KEY=""
NON_INTERACTIVE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --openai-key)
            OPENAI_KEY="$2"
            shift 2
            ;;
        --anthropic-key)
            ANTHROPIC_KEY="$2"
            shift 2
            ;;
        --non-interactive)
            NON_INTERACTIVE=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo "🔐 Updating secrets for $ENVIRONMENT environment"

# Get AWS profile and region from main deployment
cd "$MAIN_DIR"
AWS_PROFILE=$(grep '^aws_profile' terraform.tfvars | cut -d'=' -f2 | tr -d ' "' || echo "default")
AWS_REGION=$(grep '^aws_region' terraform.tfvars | cut -d'=' -f2 | tr -d ' "' || echo "us-west-2")

echo "Using AWS profile: $AWS_PROFILE"
echo "Using AWS region: $AWS_REGION"

# Verify AWS credentials
AWS_IDENTITY=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --region "$AWS_REGION" --output text --query 'Account' 2>/dev/null || echo "ERROR")
if [ "$AWS_IDENTITY" = "ERROR" ]; then
    echo "❌ Error: AWS profile '$AWS_PROFILE' is not valid"
    exit 1
fi
echo "✅ AWS Account: $AWS_IDENTITY"

# Get secrets ARN and current values
SECRETS_ARN=$(terraform output -raw secrets_arn)
echo "📋 Retrieving current secrets..."

# Extract current generated secrets
CURRENT_SECRETS=$(aws secretsmanager get-secret-value \
    --secret-id "$SECRETS_ARN" \
    --profile "$AWS_PROFILE" \
    --region "$AWS_REGION" \
    --query 'SecretString' \
    --output text)

APP_SECRET=$(echo "$CURRENT_SECRETS" | jq -r '.secret_key')
POSTGRES_PASSWORD=$(echo "$CURRENT_SECRETS" | jq -r '.postgres_password')
REDIS_TOKEN=$(echo "$CURRENT_SECRETS" | jq -r '.redis_auth_token')

# Get API keys from various sources (priority order)
get_api_key() {
    local key_name=$1
    local env_var=$2
    local current_value=""
    
    # 1. Command line argument (highest priority)
    if [ "$key_name" = "openai" ] && [ -n "$OPENAI_KEY" ]; then
        echo "$OPENAI_KEY"
        return
    elif [ "$key_name" = "anthropic" ] && [ -n "$ANTHROPIC_KEY" ]; then
        echo "$ANTHROPIC_KEY"
        return
    fi
    
    # 2. Environment variable
    current_value=$(printenv "$env_var" || echo "")
    if [ -n "$current_value" ]; then
        echo "$current_value"
        return
    fi
    
    # 3. .env file in secrets directory
    if [ -f "$SECRETS_DIR/.env" ]; then
        current_value=$(grep "^$env_var=" "$SECRETS_DIR/.env" | cut -d'=' -f2- | tr -d '"' || echo "")
        if [ -n "$current_value" ]; then
            echo "$current_value"
            return
        fi
    fi
    
    # 4. Interactive prompt (if not non-interactive)
    if [ "$NON_INTERACTIVE" = false ]; then
        echo -n "Enter $key_name API key: " >&2
        read -s current_value
        echo "" >&2
        echo "$current_value"
        return
    fi
    
    # 5. Fallback error
    echo "❌ Error: $key_name API key not provided via --$key_name-key, $env_var env var, or .env file" >&2
    echo "Available methods: command line flags, environment variables, .env file, or interactive mode" >&2
    exit 1
}

echo "🔑 Getting API keys..."
OPENAI_API_KEY=$(get_api_key "openai" "OPENAI_API_KEY")
ANTHROPIC_API_KEY=$(get_api_key "anthropic" "ANTHROPIC_API_KEY")

# Create terraform.tfvars for secrets update
cd "$SECRETS_DIR"
cat > terraform.tfvars << EOF
aws_region  = "$AWS_REGION"
aws_profile = "$AWS_PROFILE"

secrets_manager_arn = "$SECRETS_ARN"

# API keys
openai_api_key    = "$OPENAI_API_KEY"
anthropic_api_key = "$ANTHROPIC_API_KEY"

# Generated secrets (preserved)
app_secret_key    = "$APP_SECRET"
postgres_password = "$POSTGRES_PASSWORD"
redis_auth_token  = "$REDIS_TOKEN"
EOF

echo "📋 Initializing Terraform..."
terraform init -reconfigure -input=false

echo "🔍 Planning secrets update..."
terraform plan -out=secrets-plan

if [ "$NON_INTERACTIVE" = false ]; then
    echo "⚠️  About to update secrets in AWS Secrets Manager"
    echo "Press Enter to continue or Ctrl+C to cancel..."
    read -r
else
    echo "🤖 Non-interactive mode: proceeding with secrets update..."
fi

echo "🚀 Applying secrets update..."
terraform apply -auto-approve secrets-plan

# Clean up terraform.tfvars (contains secrets)
rm -f terraform.tfvars

echo "✅ Secrets updated successfully!"
echo ""
echo "Usage examples:"
echo "  Interactive:     ./update-secrets-unified.sh sandbox"
echo "  Command line:    ./update-secrets-unified.sh sandbox --openai-key 'key' --anthropic-key 'key'"
echo "  Environment:     OPENAI_API_KEY='key' ANTHROPIC_API_KEY='key' ./update-secrets-unified.sh sandbox"
echo "  CI/CD:           ./update-secrets-unified.sh sandbox --non-interactive"