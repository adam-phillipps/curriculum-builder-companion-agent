# API Reference

The Curriculum Builder API provides endpoints for content management, learning analytics, and AI-powered educational workflows.

## 🚀 Base URL

- **Development**: `http://localhost:8001`
- **API Documentation**: `http://localhost:8001/api/docs`
- **Alternative Docs**: `http://localhost:8001/api/redoc`

## 🔑 Authentication

Currently using development mode without authentication. Production deployment will include:
- JWT-based authentication
- Role-based access control
- API key management for external integrations

## 📚 Core Endpoints

### Learning Outcomes

#### Search Learning Outcomes
```http
GET /api/v1/learning-outcomes/search
```

**Parameters:**
- `query` (required): Natural language learning goal
- `max_results` (optional): Maximum suggestions (1-20, default: 10)
- `domain` (optional): Filter by domain (e.g., "programming")

**Response:**
```json
[
  {
    "outcome_id": 1,
    "name": "Python Web Development",
    "description": "Build web applications using Python frameworks",
    "domain": "programming",
    "difficulty_level": "intermediate",
    "tags": ["python", "web", "flask", "django"],
    "similarity_score": 0.85,
    "is_existing": true
  }
]
```

#### Create Learning Outcome
```http
POST /api/v1/learning-outcomes/
```

**Request Body:**
```json
{
  "name": "Machine Learning Fundamentals",
  "description": "Understand core ML concepts and algorithms",
  "domain": "data_science",
  "difficulty_level": "beginner",
  "tags": ["machine-learning", "python", "algorithms"],
  "created_by_user_id": 1
}
```

### Content Management

#### List Learning Content
```http
GET /api/v1/content
```

**Parameters:**
- `tier` (optional): Filter by tier (T1, T2, T3)
- `persona` (optional): Filter by target persona
- `content_type` (optional): Filter by type (lesson, lab, assessment)
- `skip` (optional): Pagination offset
- `limit` (optional): Results per page

#### Process Content with AI
```http
POST /api/v1/agents/process-content
```

**Request Body:**
```json
{
  "content": "Learn AWS Lambda basics with Python...",
  "model_provider": "openai",
  "model_name": "gpt-4",
  "suggested_tier": "T2",
  "suggested_personas": ["developer"],
  "suggested_content_type": "lesson"
}
```

### Progress Tracking

#### Enroll in Content
```http
POST /api/v1/progress/enroll
```

**Request Body:**
```json
{
  "user_id": 1,
  "content_id": 101
}
```

#### Update Progress
```http
PUT /api/v1/progress/update
```

**Request Body:**
```json
{
  "user_id": 1,
  "content_id": 101,
  "comprehension_percentage": 85.0,
  "status": "in_progress"
}
```

### User Management

#### Create User
```http
POST /users/
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "current_role": "learner"
}
```

#### Get User Profile
```http
GET /users/{user_id}/learner-profile
```

### Vector Search

#### Similarity Search
```http
POST /api/v1/vector/search
```

**Request Body:**
```json
{
  "query_text": "Python web development tutorial",
  "similarity_threshold": 0.3,
  "max_results": 10,
  "search_approved_only": false
}
```

## 📊 Response Formats

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "status": "error",
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid input parameters",
  "details": { ... }
}
```

## 🔄 Workflow Endpoints

### Content Processing Workflow
```http
POST /api/v1/agents/process-content
```

**Workflow Steps:**
1. **Metadata Extraction**: AI analyzes content and extracts learning objectives
2. **Similarity Check**: Compares against existing content
3. **Human Review**: Flags content requiring manual review
4. **Publication**: Approved content becomes available

**Response:**
```json
{
  "workflow_id": "uuid-string",
  "status": "published|human_review|error",
  "content_id": 123,
  "extracted_metadata": { ... },
  "similar_content": [ ... ],
  "human_review_required": false
}
```

## 📈 Analytics Endpoints

### Gap Analysis
```http
POST /api/v1/analysis/gap-analysis
```

**Request Body:**
```json
{
  "user_id": 1,
  "target_outcome_id": 5,
  "current_skills": ["python_basics", "web_fundamentals"]
}
```

### Learning Pathway
```http
GET /users/{user_id}/content-progress
```

Returns user's progress across all enrolled content with completion and comprehension metrics.

## 🚨 Rate Limits

- **Development**: No rate limits
- **Production**: 1000 requests/hour per API key
- **Burst**: Up to 100 requests/minute

## 📝 SDKs and Examples

### Python Example
```python
import requests

# Search for learning outcomes
response = requests.get(
    "http://localhost:8001/api/v1/learning-outcomes/search",
    params={"query": "python web development", "max_results": 5}
)
suggestions = response.json()
```

### JavaScript Example
```javascript
// Enroll in content
const response = await fetch('/api/v1/progress/enroll', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 1,
    content_id: 101
  })
});
```

## 🔧 Development

### Local Testing
```bash
# Start development environment
docker-compose up -d

# Test API endpoints
curl http://localhost:8001/health
curl http://localhost:8001/api/v1/learning-outcomes/search?query=python
```

### API Documentation
- **Interactive Docs**: http://localhost:8001/api/docs
- **ReDoc**: http://localhost:8001/api/redoc
- **OpenAPI Spec**: http://localhost:8001/openapi.json