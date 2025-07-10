# Curriculum Builder Companion Agent

> **For Product Documentation**: Visit [/docs](http://localhost:8001/docs) when running the application
> 
> **For API Documentation**: Visit [/docs](http://localhost:8001/docs) → API Reference

An AI-powered curriculum building and analysis platform built with FastAPI, PostgreSQL, ChromaDB, and Next.js. This README is for **developers and contributors**.

## 🏗️ Technical Overview

This platform provides:
- **Agentic AI workflows** for content processing and metadata extraction
- **Vector similarity search** for learning outcomes and content discovery  
- **Real-time progress tracking** with comprehension vs completion metrics
- **Interactive learning graphs** with D3.js visualization and gap analysis
- **Role-based interfaces** for learners, builders, architects, and admins

### Technical Features

- 🤖 **LangGraph Workflows** - Multi-step AI processing with state management
- 🔍 **ChromaDB Integration** - Vector similarity search with metadata filtering
- 📊 **Async SQLAlchemy** - PostgreSQL with proper connection pooling
- 🎯 **Pydantic Validation** - Type-safe API contracts and data models
- 📈 **D3.js Visualizations** - Interactive learning graphs with pan/zoom
- 🔄 **Alembic Migrations** - Database schema version control
- 🧪 **Pytest Test Suite** - 283 tests with unit/integration separation
- 🐳 **Docker Compose** - Full development environment
- ⚡ **Redis Caching** - Session management and pathway caching
- 🔒 **AGPL-3.0 License** - Prevents commercial exploitation

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │────│   PostgreSQL     │    │   ChromaDB      │
│   (Port 8001)   │    │   (Port 5432)    │    │   (Port 8000)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                         ┌──────────────────┐
                         │      Redis       │
                         │   (Port 6379)    │
                         └──────────────────┘
```

### Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL with async support
- **Vector Store**: ChromaDB for similarity search
- **Cache**: Redis for session management
- **AI/ML**: LangChain, LangGraph for agentic workflows
- **LLM Providers**: OpenAI, Anthropic (configurable)
- **Infrastructure**: Docker Compose for development

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI and/or Anthropic API keys
- Python 3.11+ (for local development)
- 8GB+ RAM recommended

### Setup

1. **Clone and configure**
   ```bash
   git clone <repository-url>
   cd curriculum-builder-companion-agent
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start development environment**
   ```bash
   # Full setup (migrations + seeding + app)
   docker-compose up -d
   
   # Or use helper commands
   ./scripts/dev-commands.sh start
   ```

3. **Verify services**
   ```bash
   docker-compose ps
   curl http://localhost:8001/health
   ```

### Services

- **FastAPI App**: http://localhost:8001
- **API Documentation**: http://localhost:8001/api/docs
- **Product Documentation**: http://localhost:8001/docs (when built)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **ChromaDB**: http://localhost:8000

## 📖 API Usage

### Process Learning Content

Submit content for AI-powered processing and metadata extraction:

```bash
curl -X POST "http://localhost:8001/api/v1/agents/process-content" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Learn AWS Lambda basics with Python. This tutorial covers serverless functions, event triggers, and deployment strategies.",
    "model_provider": "openai",
    "model_name": "gpt-4",
    "suggested_tier": "T2",
    "suggested_personas": ["developer"],
    "suggested_content_type": "lesson"
  }'
```

### Create Learning Content

Directly create learning content:

```bash
curl -X POST "http://localhost:8001/api/v1/content" \
  -H "Content-Type: application/json" \
  -d '{
    "code_title": "T2.DEV.001",
    "title": "AWS Lambda Fundamentals",
    "description": "Introduction to serverless computing with AWS Lambda",
    "content_type": "lesson",
    "tier": "T2",
    "personas": ["developer"],
    "learning_objectives": ["Understand serverless architecture", "Deploy Lambda functions"],
    "estimated_duration": 60,
    "sandbox_type": "individual",
    "aws_services": ["Lambda", "IAM"],
    "estimated_cost": 5.0
  }'
```

### Query Learning Content

```bash
curl "http://localhost:8001/api/v1/content?tier=T2&persona=developer&limit=10"
```

## 🧪 Testing

### Test Commands

```bash
# Run all tests (283 tests)
docker-compose run --rm app test

# Run only unit tests (fast)
docker-compose run --rm -e TEST_TYPE=unit app test

# Run only integration tests
docker-compose run --rm -e TEST_TYPE=integration app test

# Or use helper commands
./scripts/dev-commands.sh test
./scripts/dev-commands.sh test-unit
./scripts/dev-commands.sh test-integration
```

### Test Organization

- **Unit Tests** (`tests/unit/`): Mock external dependencies, fast execution
- **Integration Tests** (`tests/integration/`): Real services, comprehensive workflows
- **283 total tests** with >90% coverage
- **Separated concerns**: Database, API, agents, frontend, services

### Test Strategy

- **Unit Tests**: Mock all external dependencies (LLM APIs, vector store, database)
- **Integration Tests**: Test with real services but use test data
- **LLM Tests**: Separated to allow skipping during development
- **Frontend Tests**: Test API integration and UI behavior

### Benefits of Test Organization

- **Faster iteration**: Run unit tests quickly during development
- **Efficient CI/CD**: Skip expensive integration tests when not needed
- **Clear separation**: Unit vs integration concerns are isolated
- **Service grouping**: Related tests are co-located for easier maintenance

## 🛠️ Development

### Container Commands

```bash
# Application management
docker-compose run --rm app app-minimal    # App only
docker-compose run --rm app migrate        # Run migrations
docker-compose run --rm app seed           # Seed database
docker-compose run --rm app docs           # Build documentation

# Development helpers
./scripts/dev-commands.sh start            # Full environment
./scripts/dev-commands.sh shell            # Interactive shell
./scripts/dev-commands.sh logs             # View logs
./scripts/dev-commands.sh clean            # Clean containers
```

### Key Features

- **Learning Outcomes**: AI-powered goal discovery with similarity search
- **Progress Tracking**: Dual metrics (completion vs comprehension)
- **Interactive Graphs**: D3.js visualizations with gap analysis
- **Content Builder**: Embedded similarity search and AI assistance
- **Vector Search**: ChromaDB integration for semantic matching
- **Agentic Workflows**: LangGraph-based content processing

### Project Structure

```
src/
├── agents/           # LangGraph workflows and AI agents
├── api/             # FastAPI routes and dependencies
├── db/              # Database models, CRUD operations
├── services/        # Business logic and external integrations
├── config.py        # Configuration and constants
└── main.py          # FastAPI application entry point

docs/                # MkDocs documentation
├── product/         # User-facing documentation
├── technical/       # Developer documentation
└── tutorials/       # Guides and examples

scripts/
├── entrypoint.sh    # Container entrypoint with command handling
├── dev-commands.sh  # Development helper commands
├── migrate.py       # Database migrations
└── generate_*.py    # Test data generation

tests/
├── unit/            # Unit tests (mocked dependencies)
├── integration/     # Integration tests (real services)
└── conftest.py      # Shared test fixtures
```

## 📜 Database Management

### Migrations

```bash
# Run migrations (recommended)
docker-compose run --rm app migrate

# Create new migration
docker-compose exec app alembic revision -m "description"

# View migration history
docker-compose exec app alembic history
```

### Test Data

```bash
# Seed with complex pathway data
docker-compose run --rm app seed

# Generate specific pathway types
docker-compose exec app python scripts/generate_pathway_data.py --type complex
docker-compose exec app python scripts/generate_pathway_data.py --type simple
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U curriculum_user -d curriculum_builder

# Common queries
SELECT COUNT(*) FROM learning_content;
SELECT * FROM users ORDER BY created_at DESC LIMIT 5;
SELECT * FROM learning_outcomes WHERE status = 'approved';
```

### Architecture Components

- **FastAPI Application** (`src/main.py`): ASGI app with OpenAPI documentation
- **Database Layer** (`src/db/`): Async SQLAlchemy with Alembic migrations
- **AI Agents** (`src/agents/`): LangGraph workflows for content processing
- **Vector Store** (`src/services/vector_store.py`): ChromaDB similarity search
- **API Routes** (`src/api/routes/`): RESTful endpoints with Pydantic validation
- **Frontend** (`frontend/`): Next.js with TypeScript and Tailwind CSS
- **Documentation** (`docs/`): MkDocs Material for product and technical docs

### Development Workflow

1. **Database Changes**:
   ```bash
   # Update models in src/db/models/
   docker-compose exec app alembic revision -m "description"
   docker-compose run --rm app migrate
   ```

2. **API Development**:
   ```bash
   # Add routes in src/api/routes/
   # Test endpoints
   curl http://localhost:8001/api/v1/your-endpoint
   ```

3. **Testing**:
   ```bash
   # Add tests in tests/unit/ or tests/integration/
   docker-compose run --rm app test
   ```

4. **Documentation**:
   ```bash
   # Update docs/ content
   docker-compose run --rm -e BUILD_DOCS=true app docs
   ```

### Environment Configuration

```bash
# Required API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Database (auto-configured for Docker)
POSTGRES_DB=curriculum_builder
POSTGRES_USER=curriculum_user
POSTGRES_PASSWORD=curriculum_pass

# Application Settings
AGENT_MODEL=gpt-4
SIMILARITY_THRESHOLD=0.85
HUMAN_REVIEW_REQUIRED=true

# Container Settings (for entrypoint.sh)
RELOAD=true              # Development auto-reload
SEED_DATABASE=true       # Generate test data
BUILD_DOCS=false         # Build documentation
WORKERS=1                # Uvicorn workers
```

## 📊 Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:8001/health

# Service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### Performance

- **API Response Times**: <200ms for most endpoints
- **Vector Search**: <500ms with ChromaDB
- **Database Queries**: Optimized with proper indexes
- **Memory Usage**: ~2GB for full development stack

## 🔧 Production Deployment

### AWS Infrastructure (Planned)

- **ECS/Fargate**: Container orchestration
- **RDS PostgreSQL**: Managed database
- **ElastiCache Redis**: Managed cache
- **Application Load Balancer**: Traffic distribution
- **CloudWatch**: Monitoring and logging

### Terraform IaC

Infrastructure as Code will be provided for AWS deployment with:
- Auto-scaling groups
- Security groups and VPC configuration
- Database backups and monitoring
- CI/CD pipeline integration

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes and add tests**
4. **Run tests locally**
   ```bash
   docker-compose exec app pytest
   ```
5. **Submit a pull request**

### Code Standards

- **Python**: Follow PEP 8, use type hints
- **FastAPI**: Use dependency injection, proper HTTP status codes
- **Database**: Use async SQLAlchemy, proper migrations
- **Tests**: Maintain >90% coverage, use pytest fixtures
- **Documentation**: Update README and API docs

### Commit Messages

Use conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation updates
- `test:` Test additions/updates
- `refactor:` Code refactoring

## 📊 Monitoring & Observability

### Health Checks

- **Application**: `/docs` endpoint
- **Database**: Connection pooling status
- **Redis**: Ping response
- **ChromaDB**: Vector store availability

### Logging

Structured logging with:
- Request/response logging
- Agent workflow tracing
- Error tracking and alerting
- Performance metrics

## 🔒 Security

- **API Keys**: Environment variable management
- **Database**: Connection encryption, user permissions
- **Authentication**: JWT-based (planned)
- **Rate Limiting**: Request throttling (planned)
- **Input Validation**: Pydantic schemas for all inputs

## 📚 Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **LangChain/LangGraph**: https://python.langchain.com/
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **ChromaDB**: https://docs.trychroma.com/

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

### Why AGPL-3.0?

We chose AGPL-3.0 to ensure this educational platform remains:
- **Open Source**: Source code is always available
- **Non-Profit Friendly**: Prevents commercial exploitation and white-labeling
- **Community Driven**: Modifications must be shared back to the community
- **Network Copyleft**: Even web service deployments must provide source code

### What This Means

✅ **You CAN**:
- Use this software for educational purposes
- Modify and improve the code
- Deploy it for your organization or students
- Contribute back to the project

❌ **You CANNOT**:
- Create proprietary versions or white-label products
- Charge money for access without providing source code
- Use this as the basis for commercial educational platforms
- Hide modifications when running as a web service

### Commercial Use

If you need to use this software commercially or want different licensing terms, please contact the maintainers to discuss dual licensing options.

See the [LICENSE](LICENSE) file for the complete license text.

## 🆘 Support

For questions and support:
- Create an issue in the repository
- Check existing documentation
- Review API documentation at `/docs`

---

**Built with ❤️ for efficient learning and curriculum development**

---

## 🤝 Contributing to Open Education

This project is committed to keeping educational technology open, accessible, and community-driven. By contributing, you help ensure that quality educational tools remain free for educators and learners worldwide.

### Copyright Notice

Copyright (C) 2024-2025 Curriculum Builder Contributors

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

### Source Code Availability

As required by AGPL-3.0, if you run a modified version of this software as a web service, you must provide users with access to the complete source code of your version. This ensures the educational community benefits from all improvements and modifications.