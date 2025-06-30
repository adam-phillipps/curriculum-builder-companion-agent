#!/bin/bash

# Test runner script for curriculum builder
set -e

echo "🧪 Running Curriculum Builder Test Suite..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start test environment
echo "🏗️  Setting up test environment..."
docker compose up -d postgres redis chromadb

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run tests in container
echo "🚀 Running tests..."
docker compose run --rm app pytest tests/ -v

# Cleanup
echo "🧹 Cleaning up..."
docker compose down

echo "✅ Test suite completed!"