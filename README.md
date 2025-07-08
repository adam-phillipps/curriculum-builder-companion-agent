# Curriculum Builder Companion Agent

An AI-powered curriculum building and analysis platform that helps educators create, manage, and optimize learning content using advanced agentic workflows.

## 🎯 Overview

This platform enables:
- **Builders** to efficiently create and manage learning content with AI assistance
- **Learners** to discover optimal learning pathways based on their goals
- **Administrators** to analyze content gaps, costs, and learning effectiveness

### Key Features

- 🤖 **Agentic Workflows** - Multi-step AI processing with human-in-the-loop review
- 📊 **Metadata Extraction** - Automatic classification of difficulty, personas, and learning objectives
- 🔍 **Similarity Detection** - Prevent duplicate content with vector-based similarity matching
- 💰 **Cost Estimation** - Accurate resource cost calculations for learning pathways
- 🎯 **Dynamic Model Selection** - Support for OpenAI, Anthropic, and other LLM providers
- 📈 **Analytics & Insights** - Content coverage analysis and learning pathway optimization

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

### Run Tests

```bash
# Run all tests
docker-compose exec app pytest

# Run with coverage
docker-compose exec app pytest --cov=src

# Run specific test file
docker-compose exec app pytest tests/test_db/test_crud.py -v
```

### Test Database

Tests use SQLite in-memory database with the same models as production PostgreSQL.

## 🛠️ Development

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

**Initialize Database**
```bash
docker compose exec app python scripts/init_db.py
```

**Run Database Migrations**
```bash
docker compose exec app python scripts/migrate.py
```

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
- **Configuration** (`src/config.py`): Environment-based settings and constants
- **Scripts** (`scripts/`): Database management and test data generation utilities

### Adding New Features

1. **Database Changes**: Update models in `src/db/models/`, create migration
2. **API Endpoints**: Add routes in `src/api/routes/`
3. **Agent Workflows**: Extend workflows in `src/agents/`
4. **Tests**: Add tests in appropriate `tests/` subdirectory

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
HUMAN_REVIEW_REQUIRED=true
MAX_RETRIES=3

# Database
POSTGRES_HOST=postgres
POSTGRES_DB=curriculum_builder
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

[License information to be added]

## 🆘 Support

For questions and support:
- Create an issue in the repository
- Check existing documentation
- Review API documentation at `/docs`

---

**Built with ❤️ for efficient learning and curriculum development**