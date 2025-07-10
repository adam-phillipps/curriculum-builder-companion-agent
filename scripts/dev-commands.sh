#!/bin/bash
# Development helper commands

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

case "$1" in
    "start")
        log_info "Starting full development environment..."
        log_info "Running migrations..."
        docker compose --profile migrate up migrator
        log_info "Seeding database..."
        docker compose --profile seed up seeder
        log_info "Starting application and documentation..."
        docker compose up -d app
        docker compose --profile docs up -d docs
        ;;
    "start-minimal")
        log_info "Starting minimal application (no setup tasks)..."
        docker compose up -d app
        ;;
    "start-with-docs")
        log_info "Starting application with documentation service..."
        docker compose up -d app
        docker compose --profile docs up -d docs
        ;;
    "migrate")
        log_info "Running database migrations..."
        docker compose --profile migrate up migrator
        ;;
    "seed")
        log_info "Seeding database..."
        docker compose --profile seed up seeder
        ;;
    "docs")
        log_info "Starting documentation service..."
        docker compose --profile docs up -d docs
        ;;
    "test")
        log_info "Running tests..."
        docker compose run --rm app test
        ;;
    "test-unit")
        log_info "Running unit tests..."
        docker compose run --rm -e TEST_TYPE=unit app test
        ;;
    "test-integration")
        log_info "Running integration tests..."
        docker compose run --rm -e TEST_TYPE=integration app test
        ;;
    "shell")
        log_info "Starting interactive shell..."
        docker compose exec app shell
        ;;
    "logs")
        docker compose logs -f app
        ;;
    "stop")
        log_info "Stopping all services..."
        docker compose down
        ;;
    "clean")
        log_info "Cleaning up containers and volumes..."
        docker compose down -v
        docker system prune -f
        ;;
    "help"|"--help"|"-h")
        echo "Development Commands:"
        echo ""
        echo "  start              Start full development environment (migrate + seed + app + docs)"
        echo "  start-minimal      Start app only (no setup tasks)"
        echo "  start-with-docs    Start app with documentation service"
        echo "  migrate            Run database migrations"
        echo "  seed               Seed database with test data"
        echo "  docs               Start documentation service"
        echo "  test               Run all tests"
        echo "  test-unit          Run unit tests only"
        echo "  test-integration   Run integration tests only"
        echo "  shell              Interactive shell in app container"
        echo "  logs               Show application logs"
        echo "  stop               Stop all services"
        echo "  clean              Clean up containers and volumes"
        echo "  help               Show this help"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac