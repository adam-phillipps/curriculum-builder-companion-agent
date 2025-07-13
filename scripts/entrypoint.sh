#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Signal handling for graceful shutdown
cleanup() {
    log_info "Received shutdown signal, cleaning up..."
    if [ ! -z "$UVICORN_PID" ]; then
        kill -TERM "$UVICORN_PID" 2>/dev/null || true
        wait "$UVICORN_PID" 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGTERM SIGINT

# Function to run database migrations
run_migrations() {
    if [ "$SKIP_MIGRATIONS" = "true" ]; then
        log_warn "Skipping database migrations (SKIP_MIGRATIONS=true)"
        return 0
    fi
    
    log_info "Running database migrations..."
    python scripts/migrate.py
    if [ $? -eq 0 ]; then
        log_success "Database migrations completed"
    else
        log_error "Database migrations failed"
        exit 1
    fi
}

# Function to seed database
seed_database() {
    if [ "$SKIP_SEED" = "true" ]; then
        log_warn "Skipping database seeding (SKIP_SEED=true)"
        return 0
    fi
    
    if [ "$SEED_DATABASE" = "true" ]; then
        log_info "Seeding database with test data..."
        
        # Build seed command with environment variables
        local seed_cmd="python scripts/seed_data.py --type ${SEED_TYPE:-all}"
        
        if [ -n "$SEED_EMAIL" ]; then
            seed_cmd="$seed_cmd --email $SEED_EMAIL"
        fi
        
        if [ -n "$SEED_ROLE" ]; then
            seed_cmd="$seed_cmd --role $SEED_ROLE"
        fi
        
        log_info "Running: $seed_cmd"
        $seed_cmd
        
        if [ $? -eq 0 ]; then
            log_success "Database seeding completed"
        else
            log_warn "Database seeding failed (non-critical)"
        fi
    fi
}

# Function to build documentation
build_docs() {
    log_info "Installing documentation dependencies..."
    pip install -r requirements-docs.txt
    if [ $? -ne 0 ]; then
        log_error "Failed to install documentation dependencies"
        exit 1
    fi
    
    log_info "Building documentation..."
    mkdocs build
    if [ $? -eq 0 ]; then
        log_success "Documentation built successfully"
    else
        log_error "Documentation build failed"
        exit 1
    fi
}

# Function to start the application
start_app() {
    log_info "Starting FastAPI application..."
    
    # Default uvicorn settings
    HOST=${HOST:-"0.0.0.0"}
    PORT=${PORT:-"8000"}
    WORKERS=${WORKERS:-"1"}
    RELOAD=${RELOAD:-"false"}
    
    # Build uvicorn command
    UVICORN_CMD="uvicorn src.main:app --host $HOST --port $PORT"
    
    if [ "$RELOAD" = "true" ]; then
        UVICORN_CMD="$UVICORN_CMD --reload"
    fi
    
    if [ "$WORKERS" != "1" ] && [ "$RELOAD" != "true" ]; then
        UVICORN_CMD="$UVICORN_CMD --workers $WORKERS"
    fi
    
    log_info "Command: $UVICORN_CMD"
    
    # Start uvicorn in background to handle signals properly
    $UVICORN_CMD &
    UVICORN_PID=$!
    
    # Wait for the process
    wait $UVICORN_PID
}

# Function to run tests
run_tests() {
    log_info "Running test suite..."
    
    # If arguments provided, use first arg as test type
    if [ $# -gt 0 ]; then
        TEST_TYPE="$1"
    else
        TEST_TYPE=${TEST_TYPE:-"all"}
    fi
    
    case $TEST_TYPE in
        "unit")
            pytest tests/unit/ -v
            ;;
        "integration")
            pytest tests/integration/ -v
            ;;
        "all")
            pytest -v
            ;;
        *)
            log_error "Invalid TEST_TYPE: $TEST_TYPE (use: unit, integration, all)"
            exit 1
            ;;
    esac
}

# Main command handling
case "$1" in
    "app")
        log_info "Starting application with full setup..."
        run_migrations
        seed_database
        build_docs
        start_app
        ;;
    "app-minimal")
        log_info "Starting application (minimal setup)..."
        start_app
        ;;
    "migrate")
        log_info "Running migrations only..."
        run_migrations
        ;;
    "seed")
        log_info "Seeding database only..."
        seed_database
        ;;
    "docs")
        log_info "Building documentation..."
        build_docs
        ;;
    "test")
        shift  # Remove "test" from arguments
        run_tests "$@"
        ;;
    "shell")
        log_info "Starting interactive shell..."
        exec /bin/bash
        ;;
    "help"|"--help"|"-h")
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  app          Start application with migrations, seeding, and docs"
        echo "  app-minimal  Start application only (no migrations/seeding/docs)"
        echo "  migrate      Run database migrations only"
        echo "  seed         Seed database with test data only"
        echo "  docs         Build documentation only"
        echo "  test         Run test suite"
        echo "  shell        Start interactive bash shell"
        echo "  help         Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  SKIP_MIGRATIONS=true   Skip database migrations"
        echo "  SKIP_SEED=true         Skip database seeding"
        echo "  SEED_DATABASE=true     Enable database seeding"
        echo "  SEED_TYPE=all          Seed data type: all, pathway, progress, user"
        echo "  SEED_EMAIL=email       Target user email for seeding"
        echo "  SEED_ROLE=learner      Role for target user (default: learner)"
        echo "  BUILD_DOCS=true        Enable documentation building"
        echo "  HOST=0.0.0.0           Uvicorn host (default: 0.0.0.0)"
        echo "  PORT=8000              Uvicorn port (default: 8000)"
        echo "  WORKERS=1              Uvicorn workers (default: 1)"
        echo "  RELOAD=false           Enable auto-reload (default: false)"
        echo "  TEST_TYPE=all          Test type: unit, integration, all"
        ;;
    *)
        if [ -z "$1" ]; then
            log_error "No command specified"
        else
            log_error "Unknown command: $1"
        fi
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac