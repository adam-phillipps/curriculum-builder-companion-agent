"""
Test integration of gap analyzer with chain rule functionality.
"""
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.gap_analyzer import GapAnalyzerAgent
from src.services.gap_analysis import ContentGap, GapAnalysis

class TestGapAnalyzerChainRuleIntegration:
    """Test gap analyzer integration with chain rule calculations."""
    
    def setup_method(self):
        """Set up test data."""
        self.agent = GapAnalyzerAgent()
        
        # Mock gap analysis result
        self.mock_gap = ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='linear_algebra',
            current_content_id=2,
            prerequisite_for='neural_networks',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=['Create linear algebra content'],
            dependency_depth=3,
            path_distance=2
        )
        
        self.mock_analysis = GapAnalysis(
            pathway_id=1,
            target_persona='ml_engineer',
            end_goal='Neural Networks Mastery',
            gaps=[self.mock_gap],
            pathway_strength=0.6,
            total_missing_prerequisites=1,
            weak_support_areas=['linear_algebra'],
            weighted_gap_score=0.4,
            critical_gaps=['linear_algebra'],
            gap_distribution={'critical': 1, 'high': 0, 'medium': 0, 'low': 0}
        )
    
    @pytest.mark.asyncio
    async def test_pathway_analysis_with_chain_rule(self):
        """Test pathway analysis using chain rule calculations."""
        with patch.object(self.agent.service, 'analyze_pathway_gaps', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = self.mock_analysis
            
            mock_db = AsyncMock()
            result = await self.agent.analyze_pathway(mock_db, 1)
            
            assert result['success'] is True
            assert 'analysis' in result
            assert 'recommendations' in result
            assert 'priority_actions' in result
            
            # Verify chain rule integration
            recommendations = result['recommendations']
            assert len(recommendations) > 0
            
            # Check for weighted impact calculations
            missing_prereq_rec = next((r for r in recommendations if r['type'] == 'missing_prerequisites'), None)
            assert missing_prereq_rec is not None
            assert 'weighted_impact' in missing_prereq_rec
    
    @pytest.mark.asyncio
    async def test_domain_analysis_with_chain_rule(self):
        """Test domain analysis using chain rule calculations."""
        with patch.object(self.agent.service, 'analyze_domain_gaps', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = self.mock_analysis
            
            mock_db = AsyncMock()
            result = await self.agent.analyze_domain(
                mock_db, 
                'ml_engineer', 
                ['neural networks', 'deep learning']
            )
            
            assert result['success'] is True
            assert result['analysis'].weighted_gap_score == 0.4
            assert len(result['analysis'].critical_gaps) == 1
    
    def test_recommendation_generation_with_weights(self):
        """Test recommendation generation uses weighted scoring."""
        recommendations = self.agent._generate_recommendations(self.mock_analysis)
        
        assert len(recommendations) > 0
        
        # Check that recommendations include weighted impact
        for rec in recommendations:
            if rec['type'] in ['missing_prerequisites', 'weak_support']:
                assert 'weighted_impact' in rec
                assert isinstance(rec['weighted_impact'], (int, float))
    
    def test_action_prioritization_with_chain_rule(self):
        """Test action prioritization uses chain rule scoring."""
        actions = self.agent._prioritize_actions(self.mock_analysis)
        
        assert len(actions) > 0
        
        # Check that actions include chain rule metrics
        for action in actions:
            assert 'severity_score' in action
            assert 'outcome_weight' in action
            assert 'dependency_depth' in action
            
            # Validate score ranges
            assert 0 <= action['severity_score'] <= 1.0
            assert 0 <= action['outcome_weight'] <= 1.0

if __name__ == "__main__":
    pytest.main([__file__])