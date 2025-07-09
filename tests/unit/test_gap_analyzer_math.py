"""
Unit tests for gap analyzer agent mathematical functions.
Tests recommendation generation and prioritization logic.
"""
import pytest
from unittest.mock import MagicMock

from src.agents.gap_analyzer import GapAnalyzerAgent
from src.services.gap_analysis import GapAnalysis, ContentGap

class TestGapAnalyzerMath:
    """Test mathematical functions in gap analyzer agent."""
    
    def setup_method(self):
        """Setup test instance."""
        self.agent = GapAnalyzerAgent()
    
    def create_sample_gap(self, gap_type, severity_score=0.5, outcome_weight=0.5, dependency_depth=3):
        """Helper to create sample gaps for testing."""
        return ContentGap(
            gap_type=gap_type,
            missing_concept=f'{gap_type}_concept',
            current_content_id=1,
            prerequisite_for='test_content',
            supporting_content_count=0 if gap_type == 'missing_prerequisite' else 2,
            average_duration=60,
            average_difficulty='T2',
            similarity_scores=[0.6, 0.7] if gap_type == 'weak_support' else [],
            recommendations=[f'Fix {gap_type}'],
            gap_severity_score=severity_score,
            outcome_weight=outcome_weight,
            dependency_depth=dependency_depth,
            path_distance=2
        )
    
    def test_generate_recommendations_missing_prerequisites_high_impact(self):
        """Test recommendation generation for high-impact missing prerequisites."""
        gaps = [
            self.create_sample_gap('missing_prerequisite', severity_score=0.9, outcome_weight=0.8),
            self.create_sample_gap('missing_prerequisite', severity_score=0.7, outcome_weight=0.6)
        ]
        
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Test Pathway',
            gaps=gaps,
            pathway_strength=0.6,
            total_missing_prerequisites=2,
            weak_support_areas=[]
        )
        
        recommendations = self.agent._generate_recommendations(analysis)
        
        # Should have missing prerequisites recommendation
        missing_rec = next(rec for rec in recommendations if rec['type'] == 'missing_prerequisites')
        assert missing_rec['priority'] == 'critical'  # High impact gaps
        assert missing_rec['impact'] == 'critical'
        assert 'weighted_impact' in missing_rec
        assert missing_rec['weighted_impact'] > 1.0  # Sum of outcome weights
    
    def test_generate_recommendations_missing_prerequisites_low_impact(self):
        """Test recommendation generation for low-impact missing prerequisites."""
        gaps = [
            self.create_sample_gap('missing_prerequisite', severity_score=0.5, outcome_weight=0.4),
            self.create_sample_gap('missing_prerequisite', severity_score=0.3, outcome_weight=0.3)
        ]
        
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Test Pathway',
            gaps=gaps,
            pathway_strength=0.7,
            total_missing_prerequisites=2,
            weak_support_areas=[]
        )
        
        recommendations = self.agent._generate_recommendations(analysis)
        
        # Should have missing prerequisites recommendation with lower priority
        missing_rec = next(rec for rec in recommendations if rec['type'] == 'missing_prerequisites')
        assert missing_rec['priority'] == 'high'  # Not critical due to low impact
        assert missing_rec['impact'] == 'high'
    
    def test_generate_recommendations_weak_support_high_impact(self):
        """Test recommendation generation for high-impact weak support."""
        gaps = [
            self.create_sample_gap('weak_support', severity_score=0.8, outcome_weight=0.7),
            self.create_sample_gap('weak_support', severity_score=0.6, outcome_weight=0.5)
        ]
        
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Test Pathway',
            gaps=gaps,
            pathway_strength=0.7,
            total_missing_prerequisites=0,
            weak_support_areas=['concept1', 'concept2']
        )
        
        recommendations = self.agent._generate_recommendations(analysis)
        
        # Should have weak support recommendation with high priority
        weak_rec = next(rec for rec in recommendations if rec['type'] == 'weak_support')
        assert weak_rec['priority'] == 'high'  # High impact weak support
        assert weak_rec['impact'] == 'high'
        assert 'weighted_impact' in weak_rec
    
    def test_generate_recommendations_weak_support_low_impact(self):
        """Test recommendation generation for low-impact weak support."""
        gaps = [
            self.create_sample_gap('weak_support', severity_score=0.4, outcome_weight=0.3),
            self.create_sample_gap('weak_support', severity_score=0.3, outcome_weight=0.2)
        ]
        
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Test Pathway',
            gaps=gaps,
            pathway_strength=0.8,
            total_missing_prerequisites=0,
            weak_support_areas=['concept1', 'concept2']
        )
        
        recommendations = self.agent._generate_recommendations(analysis)
        
        # Should have weak support recommendation with medium priority
        weak_rec = next(rec for rec in recommendations if rec['type'] == 'weak_support')
        assert weak_rec['priority'] == 'medium'  # Low impact
        assert weak_rec['impact'] == 'medium'
    
    def test_generate_recommendations_pathway_strength_critical(self):
        """Test pathway strength recommendation for critical cases."""
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Test Pathway',
            gaps=[],
            pathway_strength=0.4,  # Low strength
            total_missing_prerequisites=0,
            weak_support_areas=[],
            weighted_gap_score=0.7,  # High weighted gap score
            critical_gaps=['concept1', 'concept2', 'concept3'],
            gap_distribution={'critical': 3, 'high': 1, 'medium': 0, 'low': 0}
        )
        
        recommendations = self.agent._generate_recommendations(analysis)
        
        # Should have critical pathway strength recommendation
        strength_rec = next(rec for rec in recommendations if rec['type'] == 'pathway_strength')
        assert strength_rec['priority'] == 'critical'
        assert strength_rec['impact'] == 'critical'
        assert 'gap_distribution' in strength_rec
    
    def test_generate_recommendations_pathway_strength_medium(self):
        """Test pathway strength recommendation for medium cases."""
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Test Pathway',
            gaps=[],
            pathway_strength=0.6,  # Medium strength
            total_missing_prerequisites=0,
            weak_support_areas=[],
            weighted_gap_score=0.3,  # Low weighted gap score
            critical_gaps=['concept1'],
            gap_distribution={'critical': 0, 'high': 1, 'medium': 2, 'low': 1}
        )
        
        recommendations = self.agent._generate_recommendations(analysis)
        
        # Should have medium pathway strength recommendation
        strength_rec = next(rec for rec in recommendations if rec['type'] == 'pathway_strength')
        assert strength_rec['priority'] == 'medium'
        assert strength_rec['impact'] == 'medium'
    
    def test_prioritize_actions_sorting_by_weighted_score(self):
        """Test action prioritization sorts by weighted severity score."""
        gaps = [
            self.create_sample_gap('missing_prerequisite', severity_score=0.6, outcome_weight=0.5),  # 0.3
            self.create_sample_gap('missing_prerequisite', severity_score=0.9, outcome_weight=0.8),  # 0.72
            self.create_sample_gap('weak_support', severity_score=0.8, outcome_weight=0.6),         # 0.48
        ]
        
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Test Pathway',
            gaps=gaps,
            pathway_strength=0.6,
            total_missing_prerequisites=2,
            weak_support_areas=['concept']
        )
        
        actions = self.agent._prioritize_actions(analysis)
        
        # Should be sorted by severity * outcome_weight (descending)
        assert len(actions) >= 3
        
        # First action should be highest weighted missing prerequisite
        first_action = actions[0]
        assert first_action['priority'] == 1
        assert first_action['action'] == 'create_content'
        assert first_action['severity_score'] == 0.9
        assert first_action['outcome_weight'] == 0.8
    
    def test_prioritize_actions_effort_estimation(self):
        """Test action prioritization estimates effort based on dependency depth."""
        gaps = [
            self.create_sample_gap('missing_prerequisite', dependency_depth=2),  # Low dependency
            self.create_sample_gap('missing_prerequisite', dependency_depth=8),  # High dependency
        ]
        
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Test Pathway',
            gaps=gaps,
            pathway_strength=0.6,
            total_missing_prerequisites=2,
            weak_support_areas=[]
        )
        
        actions = self.agent._prioritize_actions(analysis)
        
        # Find actions by dependency depth
        low_dep_action = next(a for a in actions if a['dependency_depth'] == 2)
        high_dep_action = next(a for a in actions if a['dependency_depth'] == 8)
        
        assert low_dep_action['estimated_effort'] == 'medium'
        assert high_dep_action['estimated_effort'] == 'high'
    
    def test_prioritize_actions_impact_classification(self):
        """Test action prioritization classifies impact correctly."""
        gaps = [
            self.create_sample_gap('missing_prerequisite', severity_score=0.9, outcome_weight=0.9),  # 0.81 - critical
            self.create_sample_gap('missing_prerequisite', severity_score=0.7, outcome_weight=0.8),  # 0.56 - high
            self.create_sample_gap('weak_support', severity_score=0.8, outcome_weight=0.7),         # 0.56 - high
            self.create_sample_gap('weak_support', severity_score=0.5, outcome_weight=0.5),         # 0.25 - moderate
        ]
        
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Test Pathway',
            gaps=gaps,
            pathway_strength=0.5,
            total_missing_prerequisites=2,
            weak_support_areas=['concept1', 'concept2']
        )
        
        actions = self.agent._prioritize_actions(analysis)
        
        # Check impact classification
        critical_actions = [a for a in actions if a['impact'] == 'critical']
        high_actions = [a for a in actions if a['impact'] == 'high']
        moderate_actions = [a for a in actions if a['impact'] == 'moderate']
        
        assert len(critical_actions) >= 1  # Should have at least one critical
        assert len(high_actions) >= 1      # Should have high impact actions
        assert len(moderate_actions) >= 1  # Should have moderate impact actions
    
    def test_prioritize_actions_weak_support_similarity_scoring(self):
        """Test weak support actions include similarity scoring."""
        gap = ContentGap(
            gap_type='weak_support',
            missing_concept='test_concept',
            current_content_id=1,
            prerequisite_for='test_content',
            supporting_content_count=2,
            average_duration=60,
            average_difficulty='T2',
            similarity_scores=[0.6, 0.8],  # Average = 0.7
            recommendations=['improve content'],
            gap_severity_score=0.6,
            outcome_weight=0.5,
            dependency_depth=3,
            path_distance=2
        )
        
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Test Pathway',
            gaps=[gap],
            pathway_strength=0.7,
            total_missing_prerequisites=0,
            weak_support_areas=['test_concept']
        )
        
        actions = self.agent._prioritize_actions(analysis)
        
        # Should have weak support action with similarity score
        weak_action = next(a for a in actions if a['action'] == 'improve_content')
        assert 'avg_similarity' in weak_action
        assert abs(weak_action['avg_similarity'] - 0.7) < 0.01
    
    def test_prioritize_actions_empty_gaps(self):
        """Test action prioritization with no gaps."""
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Perfect Pathway',
            gaps=[],
            pathway_strength=1.0,
            total_missing_prerequisites=0,
            weak_support_areas=[]
        )
        
        actions = self.agent._prioritize_actions(analysis)
        
        assert len(actions) == 0  # No actions needed for perfect pathway
    
    def test_prioritize_actions_limits_results(self):
        """Test action prioritization limits results to top items."""
        # Create many gaps
        gaps = []
        for i in range(10):
            gaps.append(self.create_sample_gap('missing_prerequisite', severity_score=0.5 + i*0.05))
            gaps.append(self.create_sample_gap('weak_support', severity_score=0.4 + i*0.04))
        
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Large Pathway',
            gaps=gaps,
            pathway_strength=0.3,
            total_missing_prerequisites=10,
            weak_support_areas=[f'concept{i}' for i in range(10)]
        )
        
        actions = self.agent._prioritize_actions(analysis)
        
        # Should limit to top 3 of each type (6 total max)
        create_actions = [a for a in actions if a['action'] == 'create_content']
        improve_actions = [a for a in actions if a['action'] == 'improve_content']
        
        assert len(create_actions) <= 3
        assert len(improve_actions) <= 3
        assert len(actions) <= 6
    
    def test_recommendation_weighted_impact_calculation(self):
        """Test recommendation weighted impact is calculated correctly."""
        gaps = [
            self.create_sample_gap('missing_prerequisite', outcome_weight=0.8),
            self.create_sample_gap('missing_prerequisite', outcome_weight=0.6),
            self.create_sample_gap('missing_prerequisite', outcome_weight=0.7),
            self.create_sample_gap('missing_prerequisite', outcome_weight=0.5),
            self.create_sample_gap('missing_prerequisite', outcome_weight=0.9),
            self.create_sample_gap('missing_prerequisite', outcome_weight=0.4)  # Should be excluded (top 5 only)
        ]
        
        analysis = GapAnalysis(
            pathway_id=1,
            target_persona='developer',
            end_goal='Test Pathway',
            gaps=gaps,
            pathway_strength=0.4,
            total_missing_prerequisites=6,
            weak_support_areas=[]
        )
        
        recommendations = self.agent._generate_recommendations(analysis)
        
        missing_rec = next(rec for rec in recommendations if rec['type'] == 'missing_prerequisites')
        
        # Should sum top 5 outcome weights: 0.9 + 0.8 + 0.7 + 0.6 + 0.5 = 3.5
        expected_weighted_impact = 0.9 + 0.8 + 0.7 + 0.6 + 0.5
        assert abs(missing_rec['weighted_impact'] - expected_weighted_impact) < 0.01