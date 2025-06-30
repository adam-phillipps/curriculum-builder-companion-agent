#!/bin/bash

# Development setup script
set -e

echo "🚀 Setting up Curriculum Builder development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before continuing"
    echo "   Required: OPENAI_API_KEY and/or ANTHROPIC_API_KEY"
    exit 1
fi

# Build and start services
echo "🏗️  Building and starting services..."
docker compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker compose ps

# Run database migrations
echo "🗄️  Running database migrations..."
docker compose exec app alembic upgrade head

echo "✅ Development environment is ready!"
echo ""
echo "🌐 Services available at:"
echo "   - FastAPI App: http://localhost:8001"
echo "   - API Docs: http://localhost:8001/docs"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo "   - ChromaDB: http://localhost:8000"
echo ""
echo "🧪 Run tests with:"
echo "   docker compose exec app pytest"
echo ""
echo "📝 View logs with:"
echo "   docker compose logs -f app"