"""
Tests for Gap Analysis API routes.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import app
from src.services.gap_analysis import GapAnalysis, ContentGap

@pytest.fixture
def sample_gap_analysis():
    """Sample gap analysis result."""
    gaps = [
        ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='Python basics',
            current_content_id=1,
            prerequisite_for='Advanced Python',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=['Create T1 content for Python basics']
        )
    ]
    
    return GapAnalysis(
        pathway_id=1,
        target_persona='developer',
        end_goal='Python Development Pathway',
        gaps=gaps,
        pathway_strength=0.65,
        total_missing_prerequisites=1,
        weak_support_areas=[]
    )

@pytest.mark.asyncio
async def test_analyze_pathway_gaps_success(sample_gap_analysis):
    """Test successful pathway gap analysis API call."""
    
    with patch('src.api.routes.analysis.gap_analysis_service.analyze_pathway_gaps', return_value=sample_gap_analysis):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/analysis/pathway-gaps",
                json={"pathway_id": 1}
            )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["pathway_id"] == 1
    assert data["target_persona"] == "developer"
    assert data["pathway_strength"] == 0.65
    assert len(data["gaps"]) == 1
    assert data["gaps"][0]["gap_type"] == "missing_prerequisite"

@pytest.mark.asyncio
async def test_analyze_pathway_gaps_not_found():
    """Test pathway gap analysis with non-existent pathway."""
    
    with patch('src.api.routes.analysis.gap_analysis_service.analyze_pathway_gaps', side_effect=ValueError("Pathway 999 not found")):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/analysis/pathway-gaps",
                json={"pathway_id": 999}
            )
    
    assert response.status_code == 404
    assert "Pathway 999 not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_analyze_domain_gaps_success(sample_gap_analysis):
    """Test successful domain gap analysis API call."""
    
    # Modify sample for domain analysis
    domain_analysis = GapAnalysis(
        pathway_id=None,
        target_persona='developer',
        end_goal='Domain: Python, Web Development',
        gaps=sample_gap_analysis.gaps,
        pathway_strength=0.75,
        total_missing_prerequisites=1,
        weak_support_areas=[]
    )
    
    with patch('src.api.routes.analysis.gap_analysis_service.analyze_domain_gaps', return_value=domain_analysis):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/analysis/domain-gaps",
                json={
                    "persona": "developer",
                    "learning_objectives": ["Python", "Web Development"]
                }
            )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["pathway_id"] is None
    assert data["target_persona"] == "developer"
    assert "Domain:" in data["end_goal"]
    assert data["pathway_strength"] == 0.75

@pytest.mark.asyncio
async def test_get_gap_analysis_summary():
    """Test gap analysis summary endpoint."""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/analysis/gap-summary")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check expected fields in summary
    assert "total_pathways_analyzed" in data
    assert "total_gaps_found" in data
    assert "missing_prerequisites" in data
    assert "weak_support_areas" in data
    assert "average_pathway_strength" in data
    assert "top_missing_concepts" in data
    assert "recommendations_by_priority" in data

@pytest.mark.asyncio
async def test_analyze_pathway_gaps_invalid_request():
    """Test pathway gap analysis with invalid request data."""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/analysis/pathway-gaps",
            json={"invalid_field": "value"}
        )
    
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_analyze_domain_gaps_invalid_request():
    """Test domain gap analysis with invalid request data."""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/analysis/domain-gaps",
            json={"persona": "developer"}  # Missing learning_objectives
        )
    
    assert response.status_code == 422  # Validation error