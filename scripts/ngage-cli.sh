#!/bin/bash
set -e

# ngage-cli.sh - Unified CLI for all ngage operations
# Usage: ./scripts/ngage-cli.sh <command> [options]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Load configuration
load_config() {
    local env=${1:-local}
    
    if [ "$env" = "local" ]; then
        # Local development configuration
        export AWS_PROFILE=""
        export AWS_REGION=""
        export ECR_REPOSITORY_URL=""
        export ECS_CLUSTER=""
        export PRIVATE_SUBNETS=""
        export ECS_SECURITY_GROUP=""
        export SECRETS_ARN=""
        export IS_LOCAL=true
        log_info "Using local development environment"
        return
    fi
    
    # AWS environment configuration
    local config_file="$PROJECT_ROOT/infra/environments/$env/terraform.tfvars"
    
    if [ ! -f "$config_file" ]; then
        log_error "Configuration file not found: $config_file"
        exit 1
    fi
    
    export AWS_PROFILE=$(grep '^aws_profile' "$config_file" | cut -d'=' -f2 | tr -d ' "' || echo "default")
    export AWS_REGION=$(grep '^aws_region' "$config_file" | cut -d'=' -f2 | tr -d ' "' || echo "us-west-2")
    export IS_LOCAL=false
    
    # Get infrastructure outputs with AWS profile
    log_info "Changing to terraform directory: $PROJECT_ROOT/infra/environments/$env"
    cd "$PROJECT_ROOT/infra/environments/$env"
    
    # Set AWS profile for terraform
    log_info "Setting AWS profile: $AWS_PROFILE"
    export AWS_PROFILE="$AWS_PROFILE"
    
    log_info "Getting ECR repository URL..."
    export ECR_REPOSITORY_URL=$(AWS_PROFILE="$AWS_PROFILE" terraform output -raw ecr_repository_url 2>/dev/null || echo "")
    log_info "Setting ECS cluster name..."
    export ECS_CLUSTER="${env}-curriculum-cluster"
    log_info "Getting private subnet IDs..."
    export PRIVATE_SUBNETS=$(AWS_PROFILE="$AWS_PROFILE" terraform output -json private_subnet_ids 2>/dev/null | jq -r 'join(",")' || echo "")
    log_info "Getting ECS security group..."
    export ECS_SECURITY_GROUP=$(AWS_PROFILE="$AWS_PROFILE" terraform output -raw ecs_security_group_id 2>/dev/null || echo "")
    log_info "Getting secrets ARN..."
    export SECRETS_ARN=$(AWS_PROFILE="$AWS_PROFILE" terraform output -raw secrets_arn 2>/dev/null || echo "")
    
    # Validate required values
    if [ -z "$PRIVATE_SUBNETS" ] || [ -z "$ECS_SECURITY_GROUP" ]; then
        log_error "Missing required infrastructure outputs. Ensure terraform apply has been run."
        log_info "Private Subnets: '$PRIVATE_SUBNETS'"
        log_info "Security Group: '$ECS_SECURITY_GROUP'"
        exit 1
    fi
    
    log_info "Validation passed, returning to project root..."
    cd "$PROJECT_ROOT"
    log_info "Load config complete"
}

# Verify AWS credentials
verify_aws() {
    if [ "$IS_LOCAL" = true ]; then
        log_info "Skipping AWS verification for local environment"
        return
    fi
    
    log_info "Getting AWS account ID..."
    local account_id=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --region "$AWS_REGION" --output text --query 'Account' 2>/dev/null || echo "ERROR")
    if [ "$account_id" = "ERROR" ]; then
        log_error "AWS profile '$AWS_PROFILE' is not valid"
        exit 1
    fi
    log_info "Using AWS Account: $account_id (Profile: $AWS_PROFILE, Region: $AWS_REGION)"
    log_info "AWS verification complete"
}

# Infrastructure commands
cmd_deploy() {
    local env=${1:-sandbox}
    local auto_approve=false
    
    # Parse arguments for --auto-approve flag
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --auto-approve)
                auto_approve=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    log_info "Deploying infrastructure to $env environment"
    
    cd "$PROJECT_ROOT/infra/environments/$env"
    
    if [ ! -f "terraform.tfvars" ]; then
        log_error "terraform.tfvars not found. Copy from terraform.tfvars.example"
        exit 1
    fi
    
    terraform init -reconfigure
    terraform plan -out=tfplan
    
    if [ "$auto_approve" = true ]; then
        log_info "Auto-approving deployment..."
    else
        echo "Review the plan above. Press Enter to continue or Ctrl+C to cancel..."
        read -r
    fi
    
    terraform apply tfplan
    log_success "Infrastructure deployed successfully"
}

cmd_secrets() {
    local env=${1:-sandbox}
    local openai_key=""
    local anthropic_key=""
    local non_interactive=false
    
    # Parse arguments
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --openai-key) openai_key="$2"; shift 2 ;;
            --anthropic-key) anthropic_key="$2"; shift 2 ;;
            --non-interactive) non_interactive=true; shift ;;
            *) shift ;;
        esac
    done
    
    load_config "$env"
    verify_aws
    
    log_info "Updating secrets for $env environment"
    
    # Get current secrets
    local current_secrets=$(aws secretsmanager get-secret-value \
        --secret-id "$SECRETS_ARN" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --query 'SecretString' \
        --output text)
    
    local app_secret=$(echo "$current_secrets" | jq -r '.secret_key')\n    local postgres_password=$(echo "$current_secrets" | jq -r '.postgres_password')\n    local redis_token=$(echo "$current_secrets" | jq -r '.redis_auth_token')
    
    # Get API keys
    if [ -z "$openai_key" ]; then
        if [ "$non_interactive" = true ]; then
            openai_key=${OPENAI_API_KEY:-}
            if [ -z "$openai_key" ]; then
                log_error "OpenAI API key required (use --openai-key or OPENAI_API_KEY env var)"
                exit 1
            fi
        else
            echo -n "Enter OpenAI API key: "
            read -s openai_key
            echo
        fi
    fi
    
    if [ -z "$anthropic_key" ]; then
        if [ "$non_interactive" = true ]; then
            anthropic_key=${ANTHROPIC_API_KEY:-}
            if [ -z "$anthropic_key" ]; then
                log_error "Anthropic API key required (use --anthropic-key or ANTHROPIC_API_KEY env var)"
                exit 1
            fi
        else
            echo -n "Enter Anthropic API key: "
            read -s anthropic_key
            echo
        fi
    fi
    
    # Update secrets
    cd "$PROJECT_ROOT/infra/secrets-update"
    
    cat > terraform.tfvars << EOF
aws_region = "$AWS_REGION"
aws_profile = "$AWS_PROFILE"
secrets_manager_arn = "$SECRETS_ARN"
openai_api_key = "$openai_key"
anthropic_api_key = "$anthropic_key"
app_secret_key = "$app_secret"
postgres_password = "$postgres_password"
redis_auth_token = "$redis_token"
EOF
    
    terraform init -reconfigure -input=false
    terraform apply -auto-approve
    rm -f terraform.tfvars
    
    log_success "Secrets updated successfully"
}

build_frontend() {
    local env=$1
    local clear_cache=${2:-false}
    
    log_info "=== STARTING build_frontend function ==="
    log_info "Building frontend for $env environment using Docker"
    
    if [ "$env" = "local" ]; then
        log_info "Building frontend locally (no deployment)"
        cd "$PROJECT_ROOT"
        
        # Build using multi-stage Dockerfile frontend stage
        docker build --target frontend-builder -f Dockerfile \
            --build-arg NEXT_PUBLIC_API_URL=http://localhost:8001 \
            -t curriculum-frontend:latest .
        
        # Extract build output
        mkdir -p "$PROJECT_ROOT/frontend/out"
        docker run --rm -v "$PROJECT_ROOT/frontend/out:/output" curriculum-frontend:latest sh -c "cp -r out/* /output/ 2>/dev/null || cp -r .next/static /output/ 2>/dev/null || echo 'Build output copied'"
        
        log_success "Frontend built locally in frontend/out/"
        return
    fi
    
    # AWS deployment - need to load config for S3 operations
    log_info "Loading configuration for AWS deployment..."
    load_config "$env"
    verify_aws
    
    # Get S3 bucket from terraform output
    log_info "Getting S3 bucket name from terraform..."
    local bucket_name=$(cd "$PROJECT_ROOT/infra/environments/$env" && terraform output -raw frontend_bucket_name 2>/dev/null)
    
    if [ -z "$bucket_name" ]; then
        log_error "Could not get frontend bucket name from terraform output"
        return 1
    fi
    
    log_info "Target bucket: $bucket_name"
    
    # Build using Docker for consistency
    cd "$PROJECT_ROOT"
    
    log_info "Building frontend with Docker..."
    # Get API Gateway URL or ALB DNS name for API calls
    # Get API URL from terraform output (handles HTTPS/HTTP automatically)
    log_info "Getting API URL from terraform..."
    local api_url=$(cd "$PROJECT_ROOT/infra/environments/$env" && terraform output -raw api_url 2>/dev/null)
    
    if [ -z "$api_url" ]; then
        log_error "Could not get API URL from terraform output"
        return 1
    fi
    log_info "Got API URL: $api_url"
    
    log_info "Using API URL: $api_url"
    log_info "Starting Docker build..."
    docker build --target frontend-builder -f Dockerfile \
        --build-arg NEXT_PUBLIC_API_URL="$api_url" \
        -t curriculum-frontend:latest . || {
        log_error "Docker build failed"
        return 1
    }
    log_info "Docker build completed"
    
    # Extract build output to local directory for S3 sync
    mkdir -p "$PROJECT_ROOT/frontend/out"
    docker run --rm -v "$PROJECT_ROOT/frontend/out:/output" curriculum-frontend:latest sh -c "cp -r out/* /output/ 2>/dev/null || cp -r .next/static /output/ 2>/dev/null || echo 'Build output extracted'"
    
    log_info "Deploying to S3..."
    log_info "Using AWS region: '$AWS_REGION'"
    log_info "Using AWS profile: '$AWS_PROFILE'"
    AWS_PROFILE="$AWS_PROFILE" aws s3 sync "$PROJECT_ROOT/frontend/out/" "s3://$bucket_name/" --delete --region "$AWS_REGION"
    
    # Invalidate CloudFront cache if requested or always for deployment
    local distribution_id=$(cd "$PROJECT_ROOT/infra/environments/$env" && terraform output -raw cloudfront_distribution_id 2>/dev/null)
    
    if [ -n "$distribution_id" ] && [ "$distribution_id" != "" ]; then
        if [ "$clear_cache" = "true" ] || [ "$clear_cache" = "--clear-cache" ]; then
            log_info "Creating CloudFront invalidation (forced)..."
            local invalidation_id=$(aws cloudfront create-invalidation \
                --distribution-id "$distribution_id" \
                --paths "/*" \
                --profile "$AWS_PROFILE" \
                --region "$AWS_REGION" \
                --query 'Invalidation.Id' \
                --output text)

            log_info "Invalidation created: $invalidation_id"
            log_info "You can wait for completion with: aws cloudfront wait invalidation-completed --distribution-id $distribution_id --id $invalidation_id --profile $AWS_PROFILE"
        else
            log_info "Invalidating CloudFront cache..."
            aws cloudfront create-invalidation --distribution-id "$distribution_id" --paths "/*" --profile "$AWS_PROFILE" --region "$AWS_REGION" >/dev/null
        fi
    fi
    
    log_success "Frontend deployed successfully"
}

build_frontend_inspect() {
    local env=$1
    
    log_info "Building frontend for inspection (env: $env)"
    
    # Get ALB DNS name from terraform output if not local
    local api_url="http://localhost:8001"
    if [ "$env" != "local" ]; then
        load_config "$env"
        verify_aws
        
        local api_endpoint=$(cd "$PROJECT_ROOT/infra/environments/$env" && terraform output -raw api_gateway_url 2>/dev/null)

        if [ -z "$api_endpoint" ]; then
            # Fallback to ALB
            local alb_dns=$(cd "$PROJECT_ROOT/infra/environments/$env" && terraform output -raw alb_dns_name 2>/dev/null)
            if [ -n "$alb_dns" ]; then
                api_url="http://$alb_dns"
            fi
        else
            api_url="$api_endpoint"
        fi
        
        if [ "$api_url" != "http://localhost:8001" ]; then
            log_info "Using API URL: $api_url"
        fi
    fi
    
    cd "$PROJECT_ROOT"
    
    log_info "Building frontend with Docker for inspection..."
    docker build --target frontend-builder -f Dockerfile \
        --build-arg NEXT_PUBLIC_API_URL="$api_url" \
        -t curriculum-frontend-inspect:latest .
    
    # Extract build output to local directory for inspection
    local inspect_dir="$PROJECT_ROOT/frontend-inspect"
    mkdir -p "$inspect_dir"
    
    log_info "Extracting build files to $inspect_dir"
    docker run --rm -v "$inspect_dir:/output" curriculum-frontend-inspect:latest sh -c "cp -r out/* /output/ 2>/dev/null || cp -r .next/static /output/ 2>/dev/null || echo 'Build output extracted'"
    
    log_success "Frontend built for inspection in: $inspect_dir"
    log_info "You can now inspect files like: $inspect_dir/_next/static/chunks/pages/*.js"
}

build_local_image() {
    local image_name=$1
    local increment_type=$2
    
    local dockerfile="Dockerfile"
    case $image_name in
        "curriculum-migrate") dockerfile="Dockerfile.migrate" ;;
        "curriculum-docs") dockerfile="Dockerfile.docs" ;;
    esac
    
    local version="v1.0.0-dev"
    
    log_info "Building $image_name locally with Dockerfile: $dockerfile"
    log_info "Local tags: latest and $version"
    
    # Build image for local use
    docker build -f "$dockerfile" -t "$image_name:latest" -t "$image_name:$version" "$PROJECT_ROOT"
    
    log_success "Local image built: $image_name:latest"
    log_success "Local image built: $image_name:$version"
}

get_next_version() {
    local image_name=$1
    local increment_type=$2
    local repo_url=$3
    
    # Get repository name from URL
    local repo_name=$(basename "$repo_url" | cut -d: -f1)
    
    # Get latest semantic version from ECR
    local latest_version=$(aws ecr describe-images \
        --repository-name "$repo_name" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --query "imageDetails[].imageTags[]" \
        --output text 2>/dev/null | \
        grep -E "^v[0-9]+\.[0-9]+\.[0-9]+$" | \
        sed "s/v//" | \
        sort -V | tail -n1)
    
    if [ -z "$latest_version" ]; then
        echo "v1.0.0"
        return
    fi
    
    local major=$(echo $latest_version | cut -d. -f1)
    local minor=$(echo $latest_version | cut -d. -f2)
    local patch=$(echo $latest_version | cut -d. -f3)
    
    case $increment_type in
        "major")
            echo "v$((major + 1)).0.0"
            ;;
        "minor")
            echo "v$major.$((minor + 1)).0"
            ;;
        "patch"|*)
            echo "v$major.$minor.$((patch + 1))"
            ;;
    esac
}

build_image_stage() {
    local image_name=$1
    local stage_name=$2
    local increment_type=$3
    local repo_url=$4
    
    local version=$(get_next_version "$image_name" "$increment_type" "$repo_url")
    
    log_info "Building $image_name (stage: $stage_name) with version $version"
    
    # Build specific stage from multi-stage Dockerfile
    docker build --target "$stage_name" -f "Dockerfile" -t "$image_name:latest" -t "$image_name:$version" "$PROJECT_ROOT"
    
    # Tag for ECR
    docker tag "$image_name:latest" "$repo_url:latest"
    docker tag "$image_name:$version" "$repo_url:$version"
    
    # Push both tags
    docker push "$repo_url:latest"
    docker push "$repo_url:$version"
    
    log_success "Image pushed: $repo_url:latest"
    log_success "Image pushed: $repo_url:$version"
}

build_image() {
    local image_name=$1
    local dockerfile=$2
    local increment_type=$3
    local repo_url=$4
    
    local version=$(get_next_version "$image_name" "$increment_type" "$repo_url")
    
    log_info "Building $image_name with Dockerfile: $dockerfile"
    log_info "Tags: latest and $version"
    
    # Build image with both tags (following your exact format)
    docker build -f "$dockerfile" -t "$image_name:latest" -t "$image_name:$version" "$PROJECT_ROOT"
    
    # Tag for ECR (following your exact format)
    docker tag "$image_name:latest" "$repo_url:latest"
    docker tag "$image_name:$version" "$repo_url:$version"
    
    # Push both tags (following your exact format)
    docker push "$repo_url:latest"
    docker push "$repo_url:$version"
    
    log_success "Image pushed: $repo_url:latest"
    log_success "Image pushed: $repo_url:$version"
}

restart_ecs_service() {
    local env=$1
    local service_name=$2
    
    log_info "Restarting ECS service: $service_name"
    
    aws ecs update-service \
        --cluster "${env}-curriculum-cluster" \
        --service "$service_name" \
        --force-new-deployment \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" >/dev/null
    
    log_success "ECS service restart initiated: $service_name"
}

cmd_build() {
    local env=${1:-local}
    local image_name=${2:-curriculum-api}
    local increment_type="patch"
    local restart_service=false
    local clear_cache=false
    
    log_info "=== CMD_BUILD STARTED ==="
    log_info "Environment: $env"
    log_info "Image: $image_name"
    
    # Parse remaining arguments
    shift 2
    for arg in "$@"; do
        case $arg in
            --restart)
                restart_service=true
                ;;
            --clear-cache)
                clear_cache=true
                ;;
            patch|minor|major)
                increment_type="$arg"
                ;;
        esac
    done
    
    log_info "Increment: $increment_type"
    log_info "Clear cache: $clear_cache"
    log_info "Restart service: $restart_service"
    
    # Handle local builds differently
    if [ "$env" = "local" ]; then
        build_local_image "$image_name" "$increment_type"
        return
    fi
    
    # Handle frontend builds separately (no ECR needed)
    case $image_name in
        "frontend")
            build_frontend "$env" "$clear_cache"
            return
            ;;
        "inspect-frontend")
            build_frontend_inspect "$env"
            return
            ;;
    esac
    
    # For Docker images, load config and verify AWS
    load_config "$env"
    verify_aws
    
    if [ -z "$ECR_REPOSITORY_URL" ]; then
        log_error "ECR repository URL not found. Deploy infrastructure first."
        exit 1
    fi
    
    # Get repository URLs from terraform output first
    local api_repo_url=$(cd "$PROJECT_ROOT/infra/environments/$env" && terraform output -raw curriculum_api_repository_url 2>/dev/null)
    local migrate_repo_url=$(cd "$PROJECT_ROOT/infra/environments/$env" && terraform output -raw curriculum_migrate_repository_url 2>/dev/null)
    local docs_repo_url=$(cd "$PROJECT_ROOT/infra/environments/$env" && terraform output -raw curriculum_docs_repository_url 2>/dev/null)
    
    # Validate we got the repository URLs
    if [ -z "$api_repo_url" ] || [ -z "$migrate_repo_url" ] || [ -z "$docs_repo_url" ]; then
        log_error "Failed to get ECR repository URLs from terraform output"
        log_info "API repo: '$api_repo_url'"
        log_info "Migrate repo: '$migrate_repo_url'"
        log_info "Docs repo: '$docs_repo_url'"
        exit 1
    fi
    
    # Authenticate with ECR (only for Docker images, not frontend)
    local ecr_registry=$(echo "$api_repo_url" | cut -d'/' -f1)
    log_info "Authenticating with ECR registry: $ecr_registry"
    aws ecr get-login-password --region "$AWS_REGION" --profile "$AWS_PROFILE" | \
        docker login --username AWS --password-stdin "$ecr_registry"
    
    case $image_name in
        "curriculum-api")
            build_image_stage "curriculum-api" "api" "$increment_type" "$api_repo_url"
            if [ "$restart_service" = true ]; then
                restart_ecs_service "$env" "${env}-curriculum-api"
            fi
            ;;
        "curriculum-migrate")
            build_image_stage "curriculum-migrate" "migrate" "$increment_type" "$migrate_repo_url"
            ;;
        "curriculum-docs")
            build_image_stage "curriculum-docs" "docs" "$increment_type" "$docs_repo_url"
            ;;

        "all")
            build_image_stage "curriculum-api" "api" "$increment_type" "$api_repo_url"
            build_image_stage "curriculum-migrate" "migrate" "$increment_type" "$migrate_repo_url"
            build_image_stage "curriculum-docs" "docs" "$increment_type" "$docs_repo_url"
            # Check for --clear-cache flag in remaining arguments
            local clear_cache=false
            shift 3 # Skip env, image_name, increment_type
            for arg in "$@"; do
                if [ "$arg" = "--clear-cache" ]; then
                    clear_cache=true
                    break
                fi
            done
            build_frontend "$env" "$clear_cache"
            ;;
        *)
            log_error "Unknown image: $image_name"
            log_info "Available images: curriculum-api, curriculum-migrate, curriculum-docs, frontend, inspect-frontend, all"
            exit 1
            ;;
    esac
}

cmd_migrate() {
    local env=${1:-local}
    
    load_config "$env"
    verify_aws
    
    log_info "Running database migration"
    
    if [ "$IS_LOCAL" = true ]; then
        # Local development migration
        log_info "Running local database migration via Docker Compose"
        cd "$PROJECT_ROOT"
        
        if ! docker compose ps postgres | grep -q "Up"; then
            log_error "PostgreSQL container is not running. Start with: docker compose up -d postgres"
            exit 1
        fi
        
        docker compose run --rm app python scripts/migrate.py
        log_success "Local database migration completed successfully"
    else
        # AWS ECS migration
        local task_arn=$(aws ecs run-task \
            --cluster "$ECS_CLUSTER" \
            --task-definition "${env}-curriculum-db-migrate" \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNETS],securityGroups=[$ECS_SECURITY_GROUP],assignPublicIp=DISABLED}" \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --query 'tasks[0].taskArn' \
            --output text)
        
        log_info "Migration task started: $task_arn"
        
        aws ecs wait tasks-stopped \
            --cluster "$ECS_CLUSTER" \
            --tasks "$task_arn" \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION"
        
        local exit_code=$(aws ecs describe-tasks \
            --cluster "$ECS_CLUSTER" \
            --tasks "$task_arn" \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --query 'tasks[0].containers[0].exitCode' \
            --output text)
        
        if [ "$exit_code" = "0" ]; then
            log_success "Database migration completed successfully"
        else
            log_error "Database migration failed with exit code: $exit_code"
            exit 1
        fi
    fi
}

cmd_docs() {
    local env=${1:-sandbox}
    
    load_config "$env"
    verify_aws
    
    log_info "Building and deploying documentation"
    
    local task_arn=$(aws ecs run-task \
        --cluster "$ECS_CLUSTER" \
        --task-definition "${env}-curriculum-docs-build" \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNETS],securityGroups=[$ECS_SECURITY_GROUP],assignPublicIp=DISABLED}" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --query 'tasks[0].taskArn' \
        --output text)
    
    log_info "Docs build task started: $task_arn"
    
    aws ecs wait tasks-stopped \
        --cluster "$ECS_CLUSTER" \
        --tasks "$task_arn" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION"
    
    local exit_code=$(aws ecs describe-tasks \
        --cluster "$ECS_CLUSTER" \
        --tasks "$task_arn" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --query 'tasks[0].containers[0].exitCode' \
        --output text)
    
    if [ "$exit_code" = "0" ]; then
        log_success "Documentation build completed successfully"
        log_info "Documentation available at: https://$(cd "$PROJECT_ROOT/infra/environments/$env" && terraform output -raw frontend_url)/docs/"
    else
        log_error "Documentation build failed with exit code: $exit_code"
        exit 1
    fi
}

cmd_seed() {
    local env=${1:-local}
    local data_type=${2:-all}
    local email=""
    local role="learner"
    
    # Parse additional arguments
    shift 2
    while [[ $# -gt 0 ]]; do
        case $1 in
            --email)
                email="$2"
                shift 2
                ;;
            --role)
                role="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    load_config "$env"
    
    log_info "Seeding database with $data_type data"
    if [ -n "$email" ]; then
        log_info "Target user: $email (role: $role)"
    fi
    
    if [ "$IS_LOCAL" = true ]; then
        cd "$PROJECT_ROOT"
        
        if ! docker compose ps postgres | grep -q "Up"; then
            log_error "PostgreSQL container is not running. Start with: docker compose up -d postgres"
            exit 1
        fi
        
        # Use entrypoint script for consistency
        local env_vars="-e SEED_DATABASE=true -e SEED_TYPE=$data_type"
        if [ -n "$email" ]; then
            env_vars="$env_vars -e SEED_EMAIL=$email -e SEED_ROLE=$role"
        fi
        
        docker compose run --rm $env_vars app seed
        log_success "Local database seeded successfully"
    else
        # AWS ECS task execution
        log_info "Running seed task on ECS"
        
        # Build environment variables for ECS task
        local env_overrides='"environment":[{"name":"SEED_DATABASE","value":"true"},{"name":"SEED_TYPE","value":"'$data_type'"}'
        if [ -n "$email" ]; then
            env_overrides="$env_overrides,{\"name\":\"SEED_EMAIL\",\"value\":\"$email\"},{\"name\":\"SEED_ROLE\",\"value\":\"$role\"}"
        fi
        env_overrides="$env_overrides]"
        
        local task_arn=$(aws ecs run-task \
            --cluster "$ECS_CLUSTER" \
            --task-definition "${env}-curriculum-db-migrate" \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNETS],securityGroups=[$ECS_SECURITY_GROUP],assignPublicIp=DISABLED}" \
            --overrides "{\"containerOverrides\":[{\"name\":\"db-migrate\",\"command\":[\"./scripts/entrypoint.sh\",\"seed\"],$env_overrides}]}" \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --query 'tasks[0].taskArn' \
            --output text)
        
        log_info "Seed task started: $task_arn"
        
        aws ecs wait tasks-stopped \
            --cluster "$ECS_CLUSTER" \
            --tasks "$task_arn" \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION"
        
        local exit_code=$(aws ecs describe-tasks \
            --cluster "$ECS_CLUSTER" \
            --tasks "$task_arn" \
            --profile "$AWS_PROFILE" \
            --region "$AWS_REGION" \
            --query 'tasks[0].containers[0].exitCode' \
            --output text)
        
        if [ "$exit_code" = "0" ]; then
            log_success "Database seeding completed successfully"
        else
            log_error "Database seeding failed with exit code: $exit_code"
            log_info "Check logs with: $0 logs $env migrate"
            exit 1
        fi
    fi
}

cmd_dev() {
    local action=${1:-start}
    
    cd "$PROJECT_ROOT"
    
    case $action in
        "start")
            log_info "Starting full development environment"
            docker compose up -d
            ;;
        "stop")
            log_info "Stopping development environment"
            docker compose down
            ;;
        "clean")
            log_info "Cleaning development environment"
            docker compose down -v
            docker system prune -f
            ;;
        "logs")
            docker compose logs -f app
            ;;
        "shell")
            docker compose exec app bash
            ;;
        *)
            log_error "Unknown dev action: $action. Use: start, stop, clean, logs, shell"
            exit 1
            ;;
    esac
}

cmd_logs() {
    local env=${1:-sandbox}
    local service=${2:-migrate}
    
    load_config "$env"
    verify_aws
    
    if [ "$IS_LOCAL" = true ]; then
        log_info "Showing local Docker logs for $service"
        cd "$PROJECT_ROOT"
        docker compose logs -f "$service" 2>/dev/null || docker compose logs -f app
        return
    fi
    
    log_info "Fetching CloudWatch logs for $service"
    
    local log_group="/ecs/sandbox-curriculum-api"
    local log_stream_prefix
    
    case $service in
        "migrate"|"db-migrate")
            log_stream_prefix="db-migrate"
            ;;
        "docs"|"docs-build")
            log_stream_prefix="docs-build"
            ;;
        "api")
            log_stream_prefix="ecs"
            ;;
        *)
            log_stream_prefix="$service"
            ;;
    esac
    
    # Get most recent log stream for the service
    local latest_stream=$(aws logs describe-log-streams \
        --log-group-name "$log_group" \
        --order-by LastEventTime \
        --descending \
        --max-items 1 \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --query "logStreams[?contains(logStreamName, '$log_stream_prefix')].logStreamName" \
        --output text 2>/dev/null)
    
    if [ -z "$latest_stream" ] || [ "$latest_stream" = "None" ]; then
        log_error "No recent log streams found for $service"
        log_info "Use this command to see all streams:"
        echo "aws logs describe-log-streams --log-group-name '$log_group' --profile '$AWS_PROFILE' --region '$AWS_REGION' --query 'logStreams[].logStreamName' --output table"
        return 1
    fi
    
    log_info "Showing recent logs from: $latest_stream"
    
    aws logs get-log-events \
        --log-group-name "$log_group" \
        --log-stream-name "$latest_stream" \
        --start-time $(($(date +%s) * 1000 - 3600000)) \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --query 'events[].[timestamp,message]' \
        --output table
}

cmd_test_cors() {
    local env=${1:-sandbox}

    load_config "$env"
    verify_aws

    if [ "$IS_LOCAL" = true ]; then
        log_info "Testing local CORS configuration"
        local api_url="http://localhost:8001"
        local origin="http://localhost:3000"
    else
        # Get API endpoint
        # Get API URL from terraform output (handles HTTPS/HTTP automatically)
        local api_url=$(cd "$PROJECT_ROOT/infra/environments/$env" && terraform output -raw api_url 2>/dev/null)

        # Get frontend URL for origin test
        local frontend_url=$(cd "$PROJECT_ROOT/infra/environments/$env" && terraform output -raw frontend_url 2>/dev/null)
        # Use frontend URL as-is (already includes https://)
        local origin="$frontend_url"
    fi

    log_info "Testing CORS from origin: $origin"
    log_info "Testing API endpoint: $api_url"

    # Test CORS preflight
    local cors_response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Origin: $origin" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS "$api_url/api/v1/health" 2>/dev/null || echo "000")

    if [ "$cors_response" = "200" ] || [ "$cors_response" = "204" ]; then
        log_success "CORS preflight test passed (HTTP $cors_response)"
    else
        log_error "CORS preflight test failed (HTTP $cors_response)"
        log_info "Try rebuilding frontend with: $0 build $env frontend --clear-cache"
        return 1
    fi

    # Test actual API call
    local api_response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Origin: $origin" \
        "$api_url/health" 2>/dev/null || echo "000")

    if [ "$api_response" = "200" ]; then
        log_success "API health check passed (HTTP $api_response)"
        log_success "CORS configuration is working correctly"
    else
        log_error "API health check failed (HTTP $api_response)"
        return 1
    fi
}

cmd_test_db() {
    local env=${1:-sandbox}
    
    load_config "$env"
    verify_aws
    
    if [ "$IS_LOCAL" = true ]; then
        log_info "Testing local database connection"
        cd "$PROJECT_ROOT"
        docker compose run --rm app python scripts/test_db_connection.py
        return
    fi
    
    log_info "Testing database connectivity via ECS task"
    
    # Run test using the migration task definition with different command
    local task_arn=$(aws ecs run-task \
        --cluster "$ECS_CLUSTER" \
        --task-definition "${env}-curriculum-db-migrate" \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNETS],securityGroups=[$ECS_SECURITY_GROUP],assignPublicIp=DISABLED}" \
        --overrides '{"containerOverrides":[{"name":"db-migrate","command":["python","scripts/test_db_connection.py"]}]}' \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --query 'tasks[0].taskArn' \
        --output text)
    
    log_info "DB test task started: $task_arn"
    
    aws ecs wait tasks-stopped \
        --cluster "$ECS_CLUSTER" \
        --tasks "$task_arn" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION"
    
    local exit_code=$(aws ecs describe-tasks \
        --cluster "$ECS_CLUSTER" \
        --tasks "$task_arn" \
        --profile "$AWS_PROFILE" \
        --region "$AWS_REGION" \
        --query 'tasks[0].containers[0].exitCode' \
        --output text)
    
    if [ "$exit_code" = "0" ]; then
        log_success "Database connectivity test passed"
    else
        log_error "Database connectivity test failed with exit code: $exit_code"
        log_info "Check logs with: $0 logs $env migrate"
    fi
}

cmd_help() {
    cat << EOF
ngage CLI - Unified command interface

Usage: $0 <command> [environment] [options]

Commands:
  deploy [env] [--auto-approve] Deploy infrastructure (AWS only)
  secrets [env] [options]      Update API secrets (AWS only)
    --openai-key KEY           OpenAI API key
    --anthropic-key KEY        Anthropic API key  
    --non-interactive          Non-interactive mode
  build [env] [image] [increment] [--clear-cache] [--restart] Build and push Docker image or frontend
    Env: local (build only), sandbox, production
    Images: curriculum-api, curriculum-migrate, curriculum-docs, frontend, inspect-frontend, all
    Increment: patch, minor, major (Docker images only)
    --clear-cache: Force CloudFront invalidation for frontend builds
    --restart: Force ECS service restart after build (API only)
  migrate [env]               Run database migration (local|AWS)
  docs [env]                  Build and deploy documentation (local|AWS)
  seed [env] [type] [options] Generate test data (local|AWS)
    Types: pathway, progress, all
    Options: --email EMAIL --role ROLE
  dev [action]                Development environment management
    Actions: start, stop, clean, logs, shell
  logs [env] [service]        Show logs for service (migrate, docs, api)
  test-db [env]               Test database connectivity
  test-cors [env]             Test CORS configuration and API connectivity
  help                        Show this help

Environments:
  local                       Local Docker development (default)
  sandbox                     AWS sandbox environment
  production                  AWS production environment

Examples:
  $0 migrate                  # Local migration
  $0 migrate sandbox          # AWS migration
  $0 test-db sandbox          # Test database connection
  $0 test-cors sandbox        # Test CORS configuration
  $0 logs sandbox migrate     # Show migration logs
  $0 seed local pathway       # Generate pathway data locally
  $0 dev start               # Start local development
  $0 deploy sandbox          # Deploy to AWS
  $0 build sandbox frontend --clear-cache  # Build frontend with cache busting
  $0 secrets sandbox --openai-key "sk-..." --anthropic-key "sk-..."

Local commands work with Docker Compose, AWS commands require infra configuration.
EOF
}

# Main command dispatcher
case "${1:-help}" in
    deploy) cmd_deploy "${2:-sandbox}" "${@:3}" ;;
    secrets) cmd_secrets "${2:-sandbox}" "${@:3}" ;;
    build) cmd_build "${2:-sandbox}" "${3:-curriculum-api}" "${4:-patch}" ;;
    migrate) cmd_migrate "${2:-local}" ;;
    docs) cmd_docs "${2:-local}" ;;
    seed) cmd_seed "${2:-local}" "${3:-all}" ;;
    dev) cmd_dev "${2:-start}" ;;
    logs) cmd_logs "${2:-sandbox}" "${3:-migrate}" ;;
    test-db) cmd_test_db "${2:-sandbox}" ;;
    test-cors) cmd_test_cors "${2:-sandbox}" ;;
    help|--help|-h) cmd_help ;;
    *) log_error "Unknown command: $1"; cmd_help; exit 1 ;;
esac