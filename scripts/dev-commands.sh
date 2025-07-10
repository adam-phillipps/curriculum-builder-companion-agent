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
        log_info "Starting development environment..."
        docker-compose up -d
        ;;
    "start-with-docs")
        log_info "Starting development environment with documentation..."
        docker-compose -f docker-compose.yml -f docker-compose.override.yml up app-with-docs -d
        ;;
    "start-minimal")
        log_info "Starting minimal application (no migrations/seeding)..."
        docker-compose -f docker-compose.yml -f docker-compose.override.yml up app-minimal -d
        ;;
    "migrate")
        log_info "Running database migrations..."
        docker-compose run --rm app migrate
        ;;
    "seed")
        log_info "Seeding database..."
        docker-compose run --rm app seed
        ;;
    "test")
        log_info "Running tests..."
        docker-compose run --rm app test
        ;;
    "test-unit")
        log_info "Running unit tests..."
        docker-compose run --rm -e TEST_TYPE=unit app test
        ;;
    "test-integration")
        log_info "Running integration tests..."
        docker-compose run --rm -e TEST_TYPE=integration app test
        ;;
    "docs")
        log_info "Building documentation..."
        docker-compose run --rm app docs
        ;;
    "shell")
        log_info "Starting interactive shell..."
        docker-compose exec app shell
        ;;
    "logs")
        docker-compose logs -f app
        ;;
    "stop")
        log_info "Stopping all services..."
        docker-compose down
        ;;
    "clean")
        log_info "Cleaning up containers and volumes..."
        docker-compose down -v
        docker system prune -f
        ;;
    "help"|"--help"|"-h")
        echo "Development Commands:"
        echo ""
        echo "  start              Start full development environment"
        echo "  start-with-docs    Start with documentation building enabled"
        echo "  start-minimal      Start app only (no migrations/seeding)"
        echo "  migrate            Run database migrations"
        echo "  seed               Seed database with test data"
        echo "  test               Run all tests"
        echo "  test-unit          Run unit tests only"
        echo "  test-integration   Run integration tests only"
        echo "  docs               Build documentation"
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