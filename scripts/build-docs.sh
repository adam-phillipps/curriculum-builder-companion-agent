#!/bin/bash
"""
Build documentation using MkDocs Material
"""

echo "📚 Building documentation..."

# Install documentation dependencies
pip install -r requirements-docs.txt

# Build the documentation
mkdocs build

echo "✅ Documentation built successfully!"
echo "📖 Serve locally with: mkdocs serve"
echo "🌐 Or access via FastAPI at: http://localhost:8001/docs"