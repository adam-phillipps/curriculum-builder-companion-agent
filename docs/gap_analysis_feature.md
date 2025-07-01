# Gap Analysis Feature

## Overview

The Gap Analysis feature identifies missing prerequisites and weak supporting content areas in learning pathways and domains. It helps curriculum architects understand where content gaps exist and provides actionable recommendations for content builders.

## Key Components

### 1. Gap Analysis Service (`src/services/gap_analysis.py`)
- **Core Logic**: Analyzes learning pathway completeness
- **Gap Detection**: Identifies missing prerequisites and weak support areas
- **Vector Integration**: Uses ChromaDB for content similarity analysis
- **Strength Scoring**: Calculates pathway strength (0-1 scale)

### 2. Gap Analyzer Agent (`src/agents/gap_analyzer.py`)
- **Agent Interface**: Provides agent-based gap analysis
- **Recommendations**: Generates actionable recommendations
- **Priority Actions**: Prioritizes actions based on impact
- **State Management**: Integrates with LangGraph workflow state

### 3. API Endpoints (`src/api/routes/analysis.py`)
- `POST /analysis/pathway-gaps`: Analyze specific learning pathway
- `POST /analysis/domain-gaps`: Analyze learning domain by objectives
- `GET /analysis/gap-summary`: Get overall gap analysis summary

## Gap Types

### Missing Prerequisites
- **Definition**: No supporting content found for required concepts
- **Impact**: Critical - blocks learning progression
- **Priority**: High to Critical (based on outcome weight)
- **Action**: Create new content
- **Weighted Factors**: Dependency depth, path distance to goal

### Weak Support
- **Definition**: Insufficient supporting content (< 3 items)
- **Impact**: Moderate to High (based on outcome weight)
- **Priority**: Medium to High (based on weighted severity)
- **Action**: Add more content or improve existing
- **Weighted Factors**: Content quality (similarity scores), dependency impact

## Weighted Scoring System

### Outcome Weight (0-1)
Calculates how much each gap impacts the final learning outcome using chain rule approximation:
- **Gap Type Weight**: Missing prerequisites = 1.0, Weak support = 0.6
- **Dependency Weight**: Based on how many other concepts depend on this (0-1)
- **Distance Weight**: Closer to learning goal = higher weight (0.2-1.0)

### Gap Severity Score (0-1)
Combines multiple factors for overall gap severity:
- **Base Severity**: Missing = 1.0, Weak = 0.5
- **Quality Penalty**: Adjusts for poor similarity scores in existing content
- **Outcome Weighting**: Multiplied by outcome weight for final score

### Pathway Metrics
- **Weighted Gap Score**: Overall severity across all gaps (0-1)
- **Critical Gaps**: Top 5 highest-impact gaps
- **Gap Distribution**: Count by severity level (critical/high/medium/low)

## API Usage Examples

### Analyze Pathway Gaps
```bash
curl -X POST "http://localhost:8000/analysis/pathway-gaps" \
  -H "Content-Type: application/json" \
  -d '{"pathway_id": 1}'
```

### Analyze Domain Gaps
```bash
curl -X POST "http://localhost:8000/analysis/domain-gaps" \
  -H "Content-Type: application/json" \
  -d '{
    "persona": "developer",
    "learning_objectives": ["Python", "Web Development"]
  }'
```

## Response Structure

```json
{
  "pathway_id": 1,
  "target_persona": "developer",
  "end_goal": "Python Development Pathway",
  "gaps": [
    {
      "gap_type": "missing_prerequisite",
      "missing_concept": "Python basics",
      "prerequisite_for": "Advanced Python",
      "supporting_content_count": 0,
      "recommendations": ["Create T1 content for Python basics"],
      "outcome_weight": 0.85,
      "path_distance": 2,
      "dependency_depth": 7,
      "gap_severity_score": 0.92
    }
  ],
  "pathway_strength": 0.65,
  "total_missing_prerequisites": 1,
  "weak_support_areas": ["Data structures"],
  "weighted_gap_score": 0.73,
  "critical_gaps": ["Python basics", "Object-oriented programming"],
  "gap_distribution": {
    "critical": 2,
    "high": 1,
    "medium": 0,
    "low": 0
  }
}
```

## Integration Points

### Vector Store Integration
- Uses existing ChromaDB service for similarity search
- Leverages metadata filtering for persona/tier matching
- Extracts related concepts from content descriptions

### Database Integration  
- Queries learning content and pathway models
- Analyzes prerequisite relationships
- Enriches vector results with database metadata

### Agent Workflow Integration
- Integrates with existing LangGraph agent state
- Provides recommendations for content builders
- Supports human-in-the-loop review processes

## Testing

Comprehensive test coverage includes:
- **Service Tests**: Core gap analysis logic
- **Agent Tests**: Agent integration and recommendations
- **API Tests**: Endpoint functionality and error handling
- **Integration Tests**: End-to-end workflow testing