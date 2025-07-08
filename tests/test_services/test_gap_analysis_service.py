"""
Tests for the Gap Analysis Service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.gap_analysis import gap_analysis_service, GapAnalysis, ContentGap
from src.db.models.content import LearningContent, LearningPathway, PathwayItem

@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def sample_content():
    """Sample learning content."""
    content = MagicMock(spec=LearningContent)
    content.id = 1
    content.title = "Advanced Python"
    content.description = "Learn advanced Python concepts"
    content.tier = "T3"
    content.learning_objectives = ["OOP", "Decorators", "Metaclasses"]
    content.prerequisites = []
    content.estimated_duration = 120
    return content

@pytest.fixture
def sample_pathway(sample_content):
    """Sample learning pathway."""
    pathway = MagicMock(spec=LearningPathway)
    pathway.id = 1
    pathway.name = "Python Development"
    pathway.target_persona = "developer"
    
    # Create pathway item
    item = MagicMock(spec=PathwayItem)
    item.sequence = 1
    item.content = sample_content
    pathway.items = [item]
    
    return pathway

@pytest.mark.asyncio
async def test_analyze_pathway_gaps_success(mock_db, sample_pathway):
    """Test successful pathway gap analysis."""
    
    with patch.object(gap_analysis_service, '_get_pathway_with_content', return_value=sample_pathway), \
         patch.object(gap_analysis_service, '_analyze_content_prerequisites', return_value=[]):
        
        result = await gap_analysis_service.analyze_pathway_gaps(mock_db, pathway_id=1)
        
        assert isinstance(result, GapAnalysis)
        assert result.pathway_id == 1
        assert result.target_persona == "developer"
        assert result.end_goal == "Python Development"

@pytest.mark.asyncio
async def test_analyze_pathway_gaps_not_found(mock_db):
    """Test pathway gap analysis with non-existent pathway."""
    
    with patch.object(gap_analysis_service, '_get_pathway_with_content', return_value=None):
        
        with pytest.raises(ValueError, match="Pathway 999 not found"):
            await gap_analysis_service.analyze_pathway_gaps(mock_db, pathway_id=999)

@pytest.mark.asyncio
async def test_analyze_content_prerequisites(mock_db, sample_content):
    """Test content prerequisite analysis."""
    
    with patch.object(gap_analysis_service, '_extract_prerequisites', return_value=['Python basics']), \
         patch.object(gap_analysis_service, '_find_supporting_content', return_value=[]):
        
        gaps = await gap_analysis_service._analyze_content_prerequisites(
            mock_db, sample_content, "developer"
        )
        
        assert len(gaps) == 1
        assert gaps[0].gap_type == 'missing_prerequisite'
        assert gaps[0].missing_concept == 'Python basics'
        assert gaps[0].supporting_content_count == 0

@pytest.mark.asyncio
async def test_analyze_content_prerequisites_weak_support(mock_db, sample_content):
    """Test content prerequisite analysis with weak support."""
    
    weak_supporting_content = [
        {'content_id': 2, 'title': 'Python Intro', 'duration': 60, 'tier': 'T1', 'similarity_score': 0.7}
    ]
    
    with patch.object(gap_analysis_service, '_extract_prerequisites', return_value=['Python basics']), \
         patch.object(gap_analysis_service, '_find_supporting_content', return_value=weak_supporting_content):
        
        gaps = await gap_analysis_service._analyze_content_prerequisites(
            mock_db, sample_content, "developer"
        )
        
        assert len(gaps) == 1
        assert gaps[0].gap_type == 'weak_support'
        assert gaps[0].missing_concept == 'Python basics'
        assert gaps[0].supporting_content_count == 1

@pytest.mark.asyncio
async def test_calculate_pathway_strength():
    """Test pathway strength calculation."""
    
    pathway = MagicMock()
    pathway.items = [MagicMock(), MagicMock()]  # 2 items
    
    gaps = [
        ContentGap('missing_prerequisite', 'concept1', 1, 'content1', 0, 0, 'T1', [], []),
        ContentGap('weak_support', 'concept2', 2, 'content2', 1, 30, 'T2', [0.6], [])
    ]
    
    strength = gap_analysis_service._calculate_pathway_strength(pathway, gaps)
    
    # With 2 items, 1 missing prereq (0.8 penalty) and 1 weak support (0.3 penalty)
    # Expected: 1.0 - (1*0.8 + 1*0.3) / 2 = 1.0 - 0.55 = 0.45
    assert strength == 0.45

@pytest.mark.asyncio
async def test_calculate_average_difficulty():
    """Test average difficulty calculation."""
    
    supporting_content = [
        {'tier': 'T1'},
        {'tier': 'T2'},
        {'tier': 'T3'}
    ]
    
    avg_difficulty = gap_analysis_service._calculate_average_difficulty(supporting_content)
    
    # Average of T1(1), T2(2), T3(3) = 2.0, which maps to T2
    assert avg_difficulty == 'T2'