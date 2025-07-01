"""
Tests for the Gap Analyzer Agent.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.gap_analyzer import gap_analyzer_agent
from src.services.gap_analysis import GapAnalysis, ContentGap
from src.agents.state import AgentState

@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)

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
            recommendations=['Create T1 content for Python basics'],
            outcome_weight=0.8,
            path_distance=2,
            dependency_depth=5,
            gap_severity_score=0.9
        ),
        ContentGap(
            gap_type='weak_support',
            missing_concept='Data structures',
            current_content_id=2,
            prerequisite_for='Algorithms',
            supporting_content_count=2,
            average_duration=45,
            average_difficulty='T2',
            similarity_scores=[0.6, 0.7],
            recommendations=['Add more T2 content for Data structures'],
            outcome_weight=0.6,
            path_distance=1,
            dependency_depth=3,
            gap_severity_score=0.5
        )
    ]
    
    return GapAnalysis(
        pathway_id=1,
        target_persona='developer',
        end_goal='Python Development Pathway',
        gaps=gaps,
        pathway_strength=0.65,
        total_missing_prerequisites=1,
        weak_support_areas=['Data structures'],
        weighted_gap_score=0.7,
        critical_gaps=['Python basics'],
        gap_distribution={'critical': 1, 'high': 0, 'medium': 1, 'low': 0}
    )

@pytest.mark.asyncio
async def test_analyze_pathway_success(mock_db, sample_gap_analysis):
    """Test successful pathway gap analysis."""
    
    with patch.object(gap_analyzer_agent.service, 'analyze_pathway_gaps', return_value=sample_gap_analysis):
        result = await gap_analyzer_agent.analyze_pathway(mock_db, pathway_id=1)
        
        assert result['success'] is True
        assert result['analysis'] == sample_gap_analysis
        assert len(result['recommendations']) > 0
        assert len(result['priority_actions']) > 0
        
        # Check recommendations structure
        recommendations = result['recommendations']
        assert any(rec['type'] == 'missing_prerequisites' for rec in recommendations)
        assert any(rec['type'] == 'weak_support' for rec in recommendations)

@pytest.mark.asyncio
async def test_analyze_pathway_with_state(mock_db, sample_gap_analysis):
    """Test pathway analysis with agent state tracking."""
    
    state = AgentState(
        raw_content="test content",
        user_id="test_user",
        model_provider="openai",
        model_name="gpt-4",
        title=None,
        suggested_tier=None,
        suggested_tags=[],
        suggested_personas=[],
        suggested_content_type=None,
        suggested_duration=None,
        suggested_sandbox_type=None,
        author=None,
        co_authors=None,
        sources=None,
        artifacts=None,
        ai_assisted=None,
        extracted_metadata={},
        similar_content=[],
        similarity_score=None,
        status="pending",
        human_review_required=False,
        review_feedback=None,
        content_id=None,
        error_message=None,
        retry_count=0
    )
    
    with patch.object(gap_analyzer_agent.service, 'analyze_pathway_gaps', return_value=sample_gap_analysis):
        result = await gap_analyzer_agent.analyze_pathway(mock_db, pathway_id=1, state=state)
        
        assert result['success'] is True
        assert 'analysis_results' in state
        assert state['analysis_results']['pathway_id'] == 1
        assert state['analysis_results']['gaps_found'] == 2
        assert state['analysis_results']['pathway_strength'] == 0.65

@pytest.mark.asyncio
async def test_analyze_pathway_error(mock_db):
    """Test pathway analysis error handling."""
    
    with patch.object(gap_analyzer_agent.service, 'analyze_pathway_gaps', side_effect=Exception("Database error")):
        result = await gap_analyzer_agent.analyze_pathway(mock_db, pathway_id=1)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Database error' in result['error']
        assert result['analysis'] is None

@pytest.mark.asyncio
async def test_analyze_domain_success(mock_db, sample_gap_analysis):
    """Test successful domain gap analysis."""
    
    # Modify sample for domain analysis
    domain_analysis = GapAnalysis(
        pathway_id=None,
        target_persona='developer',
        end_goal='Domain: Python, Web Development',
        gaps=sample_gap_analysis.gaps,
        pathway_strength=0.75,
        total_missing_prerequisites=1,
        weak_support_areas=['Data structures'],
        weighted_gap_score=0.6,
        critical_gaps=['Python basics'],
        gap_distribution={'critical': 1, 'high': 0, 'medium': 1, 'low': 0}
    )
    
    with patch.object(gap_analyzer_agent.service, 'analyze_domain_gaps', return_value=domain_analysis):
        result = await gap_analyzer_agent.analyze_domain(
            mock_db, 
            persona='developer',
            learning_objectives=['Python', 'Web Development']
        )
        
        assert result['success'] is True
        assert result['analysis'] == domain_analysis
        assert len(result['recommendations']) > 0

@pytest.mark.asyncio
async def test_generate_recommendations_missing_prerequisites(sample_gap_analysis):
    """Test recommendation generation for missing prerequisites."""
    
    recommendations = gap_analyzer_agent._generate_recommendations(sample_gap_analysis)
    
    missing_prereq_rec = next(
        (rec for rec in recommendations if rec['type'] == 'missing_prerequisites'), 
        None
    )
    
    assert missing_prereq_rec is not None
    assert missing_prereq_rec['priority'] == 'critical'  # High outcome weight (0.8) makes it critical
    assert missing_prereq_rec['impact'] == 'critical'
    assert len(missing_prereq_rec['actions']) > 0
    assert 'weighted_impact' in missing_prereq_rec

@pytest.mark.asyncio
async def test_generate_recommendations_weak_support(sample_gap_analysis):
    """Test recommendation generation for weak support areas."""
    
    recommendations = gap_analyzer_agent._generate_recommendations(sample_gap_analysis)
    
    weak_support_rec = next(
        (rec for rec in recommendations if rec['type'] == 'weak_support'), 
        None
    )
    
    assert weak_support_rec is not None
    assert weak_support_rec['priority'] == 'high'  # Outcome weight (0.6) >= 0.5 makes it high
    assert weak_support_rec['impact'] == 'high'
    assert 'weighted_impact' in weak_support_rec

@pytest.mark.asyncio
async def test_generate_recommendations_low_pathway_strength():
    """Test recommendation generation for low pathway strength."""
    
    # Create analysis with low pathway strength
    low_strength_analysis = GapAnalysis(
        pathway_id=1,
        target_persona='developer',
        end_goal='Test Pathway',
        gaps=[],
        pathway_strength=0.4,  # Low strength
        total_missing_prerequisites=0,
        weak_support_areas=[],
        weighted_gap_score=0.7,  # High weighted gap score
        critical_gaps=[],
        gap_distribution={'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    )
    
    recommendations = gap_analyzer_agent._generate_recommendations(low_strength_analysis)
    
    strength_rec = next(
        (rec for rec in recommendations if rec['type'] == 'pathway_strength'), 
        None
    )
    
    assert strength_rec is not None
    assert strength_rec['priority'] == 'critical'  # Should be critical due to high weighted gap score

@pytest.mark.asyncio
async def test_prioritize_actions(sample_gap_analysis):
    """Test action prioritization logic."""
    
    actions = gap_analyzer_agent._prioritize_actions(sample_gap_analysis)
    
    # Should have actions for both missing prerequisites and weak support
    assert len(actions) > 0
    
    # Check priority ordering
    priorities = [action['priority'] for action in actions]
    assert priorities == sorted(priorities)  # Should be in priority order
    
    # Check action types
    create_actions = [a for a in actions if a['action'] == 'create_content']
    improve_actions = [a for a in actions if a['action'] == 'improve_content']
    
    assert len(create_actions) > 0  # Should have create actions for missing prereqs
    assert len(improve_actions) > 0  # Should have improve actions for weak support

@pytest.mark.asyncio
async def test_prioritize_actions_empty_gaps():
    """Test action prioritization with no gaps."""
    
    no_gaps_analysis = GapAnalysis(
        pathway_id=1,
        target_persona='developer',
        end_goal='Perfect Pathway',
        gaps=[],
        pathway_strength=1.0,
        total_missing_prerequisites=0,
        weak_support_areas=[],
        weighted_gap_score=0.0,
        critical_gaps=[],
        gap_distribution={'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    )
    
    actions = gap_analyzer_agent._prioritize_actions(no_gaps_analysis)
    
    assert len(actions) == 0  # No actions needed for perfect pathway

@pytest.mark.asyncio
async def test_prioritize_actions_effort_estimation():
    """Test effort estimation based on dependency depth."""
    gaps = [
        ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='low_dep_concept',
            current_content_id=1,
            prerequisite_for='content1',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            dependency_depth=2,
            gap_severity_score=0.7,
            outcome_weight=0.6
        ),
        ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='high_dep_concept',
            current_content_id=2,
            prerequisite_for='content2',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            dependency_depth=8,
            gap_severity_score=0.8,
            outcome_weight=0.7
        )
    ]
    
    analysis = GapAnalysis(
        pathway_id=1,
        target_persona='developer',
        end_goal='Test Pathway',
        gaps=gaps,
        pathway_strength=0.6,
        total_missing_prerequisites=2,
        weak_support_areas=[],
        weighted_gap_score=0.5,
        critical_gaps=['high_dep_concept', 'low_dep_concept'],
        gap_distribution={'critical': 0, 'high': 2, 'medium': 0, 'low': 0}
    )
    
    actions = gap_analyzer_agent._prioritize_actions(analysis)
    
    low_dep_action = next(a for a in actions if a['dependency_depth'] == 2)
    high_dep_action = next(a for a in actions if a['dependency_depth'] == 8)
    
    assert low_dep_action['estimated_effort'] == 'medium'
    assert high_dep_action['estimated_effort'] == 'high'

@pytest.mark.asyncio
async def test_prioritize_actions_impact_classification():
    """Test action impact classification thresholds."""
    gaps = [
        ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='critical_concept',
            current_content_id=1,
            prerequisite_for='content1',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            gap_severity_score=0.9,
            outcome_weight=0.9
        ),
        ContentGap(
            gap_type='weak_support',
            missing_concept='moderate_concept',
            current_content_id=3,
            prerequisite_for='content3',
            supporting_content_count=1,
            average_duration=30,
            average_difficulty='T1',
            similarity_scores=[0.5],
            recommendations=[],
            gap_severity_score=0.5,
            outcome_weight=0.5
        )
    ]
    
    analysis = GapAnalysis(
        pathway_id=1,
        target_persona='developer',
        end_goal='Test Pathway',
        gaps=gaps,
        pathway_strength=0.5,
        total_missing_prerequisites=1,
        weak_support_areas=['moderate_concept'],
        weighted_gap_score=0.6,
        critical_gaps=['critical_concept'],
        gap_distribution={'critical': 1, 'high': 0, 'medium': 1, 'low': 0}
    )
    
    actions = gap_analyzer_agent._prioritize_actions(analysis)
    
    critical_actions = [a for a in actions if a['impact'] == 'critical']
    moderate_actions = [a for a in actions if a['impact'] == 'moderate']
    
    assert len(critical_actions) >= 1
    assert len(moderate_actions) >= 1