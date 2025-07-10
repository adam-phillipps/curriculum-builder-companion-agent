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

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd curriculum-builder-companion-agent
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the development environment**
   ```bash
   ./scripts/dev-setup.sh
   ```

4. **Verify services are running**
   ```bash
   docker-compose ps
   ```

### Services

- **API Documentation**: http://localhost:8001/docs
- **FastAPI App**: http://localhost:8001
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

### Test Suite Organization

The test suite is organized into two main categories for efficient development:

```
tests/
├── unit/                    # Pure unit tests (no external dependencies)
│   ├── db/                  # Database model and CRUD tests
│   ├── services/            # Service layer tests
│   └── [test files]         # Configuration, math, and logic tests
├── integration/             # Integration tests (external services)
│   ├── agents/              # LLM integration tests
│   ├── api/                 # API endpoint tests
│   ├── frontend/            # Frontend integration tests
│   ├── services/            # External service tests (ChromaDB, etc.)
│   └── workflows/           # End-to-end workflow tests
└── conftest.py             # Shared test fixtures
```

### Test Commands

```bash
# Run all tests (219 tests, ~4 minutes)
docker compose exec app pytest

# Run only unit tests (104 tests, ~30 seconds)
docker compose exec app pytest tests/unit/

# Run only integration tests (123 tests, ~3 minutes)
docker compose exec app pytest tests/integration/

# Skip LLM tests (for faster development)
docker compose exec app pytest -m "not llm"

# Run with coverage
docker compose exec app pytest --cov=src

# Run specific test file
docker compose exec app pytest tests/unit/test_config.py -v
```

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

### New Features Added

#### Embedded Similarity Search
- **Content Builder**: Check for similar content before submission with color-coded warnings
- **Content Catalog**: Text-based similarity search with filtering capabilities
- **Removed**: Standalone similarity search tab (functionality moved to where it's needed)

#### Content Viewing System
- **Content Viewer**: Full-screen reading experience for learners
- **Content Body Storage**: Actual learning content stored in database
- **API Integration**: Proper content retrieval endpoints

#### Role-Based Interface
- **Learners**: Content catalog with similarity search for discovery
- **Builders**: Content creation form with embedded similarity checking
- **Architects & Admins**: Specialized interfaces (coming soon)

#### Database Improvements
- **Alembic Migrations**: Proper schema version control
- **Content Body Field**: Storage for actual learning content
- **Enhanced Metadata**: Author, sources, AI assistance tracking

#### Test Suite Reorganization
- **Unit/Integration Separation**: Efficient test execution
- **Service Grouping**: Tests organized by functionality
- **Mock Strategy**: Proper isolation of external dependencies

### Project Structure

```
src/
├── agents/           # LangGraph workflows and AI agents
├── api/             # FastAPI routes and dependencies
├── db/              # Database models, CRUD operations
├── config.py        # Configuration and constants
└── main.py          # FastAPI application entry point

tests/
├── test_db/         # Database and CRUD tests
└── conftest.py      # Test configuration

scripts/
├── dev-setup.sh     # Development environment setup
├── generate_pathway_data.py  # Generate test pathway data
├── generate_sankey_data.py   # Generate Sankey visualization data
├── generate_content_progress.py  # Generate user content progress data
├── init_db.py       # Initialize database
├── migrate.py       # Run database migrations
└── run-tests.sh     # Run test suite
```

## 📜 Scripts Usage

### Database Management

**Run Database Migrations** (Recommended)
```bash
docker compose exec app python scripts/migrate.py
```
Runs Alembic migrations to update database schema. Always use this for schema changes.

**Initialize Database** (Development Only)
```bash
docker compose exec app python scripts/init_db.py
```
Creates all tables from scratch. Only use for fresh development setup.

**Create New Migration**
```bash
docker compose exec app alembic revision -m "description_of_changes"
```
Generates a new Alembic migration file for schema changes.

### Test Data Generation

**Generate Simple Linear Pathway**
```bash
docker compose exec app python scripts/generate_pathway_data.py --type simple
```

**Generate Complex Multi-Branch Pathway**
```bash
docker compose exec app python scripts/generate_pathway_data.py --type complex
```

**Generate Sankey Visualization Data**
```bash
docker compose exec app python scripts/generate_sankey_data.py
```

**Generate User Content Progress Data**
```bash
# Generate progress for default user (ID=1) and content IDs 101-106
docker compose exec app python scripts/generate_content_progress.py

# Generate progress for specific user
docker compose exec app python scripts/generate_content_progress.py --user-id 2

# Generate progress for specific content IDs
docker compose exec app python scripts/generate_content_progress.py --content-ids 101 102 103

# Generate progress for specific user and content IDs
docker compose exec app python scripts/generate_content_progress.py --user-id 2 --content-ids 101 102
```

### Testing

**Run All Tests**
```bash
docker compose exec app python scripts/run-tests.sh
```

**Run Specific Test File**
```bash
docker compose exec app pytest tests/test_db/test_crud.py -v
```

**Run Tests with Coverage**
```bash
docker compose exec app pytest --cov=src
```

### Development Setup

**Complete Development Environment Setup**
```bash
./scripts/dev-setup.sh
```
Sets up the entire development environment including:
- Docker service health checks
- Environment file creation from template
- Service startup and verification
- Database migration execution
- Service endpoint information

### Pathway Data Generation Details

The `generate_pathway_data.py` script creates realistic learning pathway data for testing:

**Simple Pathway** (`--type simple`):
- Creates 4 learning content items in linear progression
- Prerequisites: 1→2→3→4
- Good for basic testing and simple visualizations
- Generates skill assessments and user progress data

**Complex Pathway** (`--type complex`):
- Creates 6 learning content items in tree structure
- Multi-branch flow: Math + Programming → ML Theory → Neural Networks
- Tree structure with proper prerequisite relationships
- Learning objectives: Mathematics Fundamentals, Programming Fundamentals, ML Theory, Neural Networks Mastery
- Generates realistic progress data with mixed completion states

**Generated Data Includes**:
- Learning pathway with target persona and duration
- Pathway items with weights, prerequisites, and completion status
- User content progress with realistic percentages and time spent
- Skill assessments across multiple categories
- Learning objectives and content relationships

### Key Components

- **Agents** (`src/agents/`): LangGraph-based workflows for content processing
- **Database** (`src/db/`): SQLAlchemy models and async CRUD operations
- **API Routes** (`src/api/`): FastAPI endpoints with dependency injection
- **Vector Store** (`src/vector_store/`): ChromaDB integration for similarity search
- **Configuration** (`src/config.py`): Environment-based settings and constants
- **Scripts** (`scripts/`): Database management and test data generation utilities
- **Frontend** (`frontend/`): Next.js application with role-based interfaces
- **Migrations** (`alembic/`): Database schema version control

### Adding New Features

1. **Database Changes**: 
   - Update models in `src/db/models/`
   - Create Alembic migration: `alembic revision -m "description"`
   - Run migration: `python scripts/migrate.py`

2. **API Endpoints**: Add routes in `src/api/routes/`

3. **Agent Workflows**: Extend workflows in `src/agents/`

4. **Frontend Components**: Add to `frontend/src/components/`

5. **Tests**: 
   - Unit tests in `tests/unit/`
   - Integration tests in `tests/integration/`
   - Mock external dependencies in unit tests

6. **Configuration**: Update `src/config.py` for new settings

### Environment Variables

Key configuration options in `.env`:

```bash
# AI Models
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
AGENT_MODEL=gpt-4
AGENT_TEMPERATURE=0.7

# Workflow Configuration
SIMILARITY_THRESHOLD=0.85
CONTENT_SIMILARITY_LOW=0.3
CONTENT_SIMILARITY_MEDIUM=0.6
CONTENT_SIMILARITY_HIGH=0.8
HUMAN_REVIEW_REQUIRED=true
MAX_RETRIES=3

# Database
POSTGRES_HOST=postgres
POSTGRES_DB=curriculum_builder
POSTGRES_USER=curriculum_user
POSTGRES_PASSWORD=curriculum_pass

# Services
CHROMA_HOST=chromadb
CHROMA_PORT=8000
REDIS_HOST=redis
REDIS_PORT=6379
```

### Database Access

**Connect to PostgreSQL Database**
```bash
# Connect via Docker container
docker compose exec postgres psql -U curriculum_user -d curriculum_builder

# Connect from host machine (if psql installed locally)
psql -h localhost -p 5432 -U curriculum_user -d curriculum_builder
```

**Common Database Queries**

```sql
-- List all tables
\dt

-- View table structure
\d learning_content
\d users
\d learning_pathways

-- Query learning content
SELECT id, title, tier, content_type, author, created_at 
FROM learning_content 
ORDER BY created_at DESC 
LIMIT 10;

-- Query users and their roles
SELECT id, first_name, last_name, email, current_role, created_at 
FROM users 
ORDER BY created_at DESC;

-- Query content with full details
SELECT id, code_title, title, description, content_type, tier, 
       personas, learning_objectives, estimated_duration, 
       sandbox_type, aws_services, estimated_cost, status
FROM learning_content 
WHERE tier = 'T2' AND content_type = 'lesson';

-- Query learning pathways with progress
SELECT lp.id, lp.name, lp.target_persona, lp.estimated_duration,
       COUNT(pi.id) as total_items,
       AVG(pi.completion_percentage) as avg_progress
FROM learning_pathways lp
LEFT JOIN pathway_items pi ON lp.id = pi.pathway_id
GROUP BY lp.id, lp.name, lp.target_persona, lp.estimated_duration;

-- Query user content progress
SELECT u.first_name, u.last_name, lc.title, 
       ucp.status, ucp.progress_percentage, ucp.time_spent_minutes
FROM user_content_progress ucp
JOIN users u ON ucp.user_id = u.id
JOIN learning_content lc ON ucp.content_id = lc.id
ORDER BY ucp.last_accessed_at DESC;

-- Query content with similarity search metadata
SELECT id, title, content_type, tier, 
       LENGTH(content_body) as content_length,
       CASE WHEN content_body IS NOT NULL THEN 'Yes' ELSE 'No' END as has_content_body
FROM learning_content 
ORDER BY created_at DESC;
```

**Database Schema Overview**

Key tables in the system:
- `learning_content` - Main content items with metadata and content body
- `users` - User accounts and profiles
- `learning_pathways` - Learning paths and curricula
- `pathway_items` - Items within learning pathways
- `user_content_progress` - User progress tracking
- `user_skill_assessments` - Skill level assessments
- `assessment_questions` - Quiz and assessment content
- `pricing_estimates` - Cost calculations for content

### Database Management Commands

```bash
# View database logs
docker compose logs postgres

# Backup database
docker compose exec postgres pg_dump -U curriculum_user curriculum_builder > backup.sql

# Restore database
docker compose exec -T postgres psql -U curriculum_user curriculum_builder < backup.sql

# Reset database (WARNING: Destroys all data)
docker compose down
docker volume rm curriculum-builder-companion-agent_postgres_data
docker compose up -d
```

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