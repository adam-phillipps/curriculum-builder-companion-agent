"""
Unit tests for gap analysis mathematical functions.
Tests the core scoring and calculation logic.
"""
import pytest
from unittest.mock import MagicMock

from src.services.gap_analysis import GapAnalysisService, ContentGap, GapAnalysis
from src.db.models.content import LearningContent

class TestGapAnalysisMath:
    """Test mathematical functions in gap analysis service."""
    
    def setup_method(self):
        """Setup test instance."""
        self.service = GapAnalysisService()
    
    def test_calculate_outcome_weight_missing_prerequisite(self):
        """Test outcome weight calculation for missing prerequisites."""
        gap = ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='Python basics',
            current_content_id=1,
            prerequisite_for='Advanced Python',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            dependency_depth=5,
            path_distance=2
        )
        
        weight = self.service._calculate_outcome_weight(gap)
        
        # Missing prerequisite should have high weight
        assert 0.7 <= weight <= 1.0
        assert isinstance(weight, float)
    
    def test_calculate_outcome_weight_weak_support(self):
        """Test outcome weight calculation for weak support."""
        gap = ContentGap(
            gap_type='weak_support',
            missing_concept='Data structures',
            current_content_id=2,
            prerequisite_for='Algorithms',
            supporting_content_count=2,
            average_duration=45,
            average_difficulty='T2',
            similarity_scores=[0.6, 0.7],
            recommendations=[],
            dependency_depth=3,
            path_distance=1
        )
        
        weight = self.service._calculate_outcome_weight(gap)
        
        # Weak support should have moderate weight
        assert 0.4 <= weight <= 0.8
        assert isinstance(weight, float)
    
    def test_calculate_outcome_weight_high_dependency(self):
        """Test outcome weight increases with dependency depth."""
        gap_low_dep = ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='concept1',
            current_content_id=1,
            prerequisite_for='content1',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            dependency_depth=1,
            path_distance=2
        )
        
        gap_high_dep = ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='concept2',
            current_content_id=2,
            prerequisite_for='content2',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            dependency_depth=8,
            path_distance=2
        )
        
        weight_low = self.service._calculate_outcome_weight(gap_low_dep)
        weight_high = self.service._calculate_outcome_weight(gap_high_dep)
        
        assert weight_high > weight_low
    
    def test_calculate_outcome_weight_path_distance_effect(self):
        """Test outcome weight decreases with path distance."""
        gap_close = ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='concept1',
            current_content_id=1,
            prerequisite_for='content1',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            dependency_depth=5,
            path_distance=1
        )
        
        gap_far = ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='concept2',
            current_content_id=2,
            prerequisite_for='content2',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            dependency_depth=5,
            path_distance=5
        )
        
        weight_close = self.service._calculate_outcome_weight(gap_close)
        weight_far = self.service._calculate_outcome_weight(gap_far)
        
        assert weight_close > weight_far
    
    def test_calculate_gap_severity_missing_prerequisite(self):
        """Test gap severity calculation for missing prerequisites."""
        gap = ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='Python basics',
            current_content_id=1,
            prerequisite_for='Advanced Python',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            outcome_weight=0.8
        )
        
        severity = self.service._calculate_gap_severity(gap)
        
        # Missing prerequisite should have high severity
        assert 0.7 <= severity <= 1.0
        assert isinstance(severity, float)
    
    def test_calculate_gap_severity_weak_support_with_poor_similarity(self):
        """Test gap severity for weak support with poor similarity scores."""
        gap = ContentGap(
            gap_type='weak_support',
            missing_concept='Data structures',
            current_content_id=2,
            prerequisite_for='Algorithms',
            supporting_content_count=2,
            average_duration=45,
            average_difficulty='T2',
            similarity_scores=[0.3, 0.4],  # Poor similarity
            recommendations=[],
            outcome_weight=0.6
        )
        
        severity = self.service._calculate_gap_severity(gap)
        
        # Should be penalized for poor similarity
        assert 0.4 <= severity <= 0.8
    
    def test_calculate_gap_severity_weak_support_with_good_similarity(self):
        """Test gap severity for weak support with good similarity scores."""
        gap = ContentGap(
            gap_type='weak_support',
            missing_concept='Data structures',
            current_content_id=2,
            prerequisite_for='Algorithms',
            supporting_content_count=2,
            average_duration=45,
            average_difficulty='T2',
            similarity_scores=[0.8, 0.9],  # Good similarity
            recommendations=[],
            outcome_weight=0.6
        )
        
        severity = self.service._calculate_gap_severity(gap)
        
        # Should have lower penalty for good similarity
        assert 0.2 <= severity <= 0.6
    
    def test_calculate_weighted_gap_score_empty_gaps(self):
        """Test weighted gap score calculation with no gaps."""
        score = self.service._calculate_weighted_gap_score([])
        assert score == 0.0
    
    def test_calculate_weighted_gap_score_single_gap(self):
        """Test weighted gap score calculation with single gap."""
        gap = ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='concept',
            current_content_id=1,
            prerequisite_for='content',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            gap_severity_score=0.8,
            outcome_weight=0.9
        )
        
        score = self.service._calculate_weighted_gap_score([gap])
        
        # Score should be weighted severity
        expected = (0.8 * 0.9) / 1  # severity * weight / max_possible
        assert abs(score - expected) < 0.01
    
    def test_calculate_weighted_gap_score_multiple_gaps(self):
        """Test weighted gap score calculation with multiple gaps."""
        gaps = [
            ContentGap(
                gap_type='missing_prerequisite',
                missing_concept='concept1',
                current_content_id=1,
                prerequisite_for='content1',
                supporting_content_count=0,
                average_duration=0,
                average_difficulty='unknown',
                similarity_scores=[],
                recommendations=[],
                gap_severity_score=0.9,
                outcome_weight=0.8
            ),
            ContentGap(
                gap_type='weak_support',
                missing_concept='concept2',
                current_content_id=2,
                prerequisite_for='content2',
                supporting_content_count=1,
                average_duration=30,
                average_difficulty='T1',
                similarity_scores=[0.5],
                recommendations=[],
                gap_severity_score=0.6,
                outcome_weight=0.7
            )
        ]
        
        score = self.service._calculate_weighted_gap_score(gaps)
        
        # Should aggregate weighted severities
        expected = (0.9 * 0.8 + 0.6 * 0.7) / 2
        assert abs(score - expected) < 0.01
    
    def test_identify_critical_gaps(self):
        """Test identification of critical gaps."""
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
                outcome_weight=0.8
            ),
            ContentGap(
                gap_type='weak_support',
                missing_concept='minor_concept',
                current_content_id=2,
                prerequisite_for='content2',
                supporting_content_count=1,
                average_duration=30,
                average_difficulty='T1',
                similarity_scores=[0.5],
                recommendations=[],
                gap_severity_score=0.3,
                outcome_weight=0.4
            ),
            ContentGap(
                gap_type='missing_prerequisite',
                missing_concept='important_concept',
                current_content_id=3,
                prerequisite_for='content3',
                supporting_content_count=0,
                average_duration=0,
                average_difficulty='unknown',
                similarity_scores=[],
                recommendations=[],
                gap_severity_score=0.7,
                outcome_weight=0.9
            )
        ]
        
        critical_gaps = self.service._identify_critical_gaps(gaps)
        
        # Should return concepts sorted by severity * weight
        assert len(critical_gaps) <= 5
        assert 'critical_concept' in critical_gaps
        assert critical_gaps[0] == 'critical_concept'  # Highest score should be first
    
    def test_calculate_gap_distribution(self):
        """Test gap distribution calculation."""
        gaps = [
            ContentGap(
                gap_type='missing_prerequisite',
                missing_concept='critical',
                current_content_id=1,
                prerequisite_for='content1',
                supporting_content_count=0,
                average_duration=0,
                average_difficulty='unknown',
                similarity_scores=[],
                recommendations=[],
                gap_severity_score=0.9  # Critical
            ),
            ContentGap(
                gap_type='missing_prerequisite',
                missing_concept='high',
                current_content_id=2,
                prerequisite_for='content2',
                supporting_content_count=0,
                average_duration=0,
                average_difficulty='unknown',
                similarity_scores=[],
                recommendations=[],
                gap_severity_score=0.7  # High
            ),
            ContentGap(
                gap_type='weak_support',
                missing_concept='medium',
                current_content_id=3,
                prerequisite_for='content3',
                supporting_content_count=1,
                average_duration=30,
                average_difficulty='T1',
                similarity_scores=[0.5],
                recommendations=[],
                gap_severity_score=0.5  # Medium
            ),
            ContentGap(
                gap_type='weak_support',
                missing_concept='low',
                current_content_id=4,
                prerequisite_for='content4',
                supporting_content_count=2,
                average_duration=45,
                average_difficulty='T2',
                similarity_scores=[0.8, 0.9],
                recommendations=[],
                gap_severity_score=0.2  # Low
            )
        ]
        
        distribution = self.service._calculate_gap_distribution(gaps)
        
        assert distribution['critical'] == 1
        assert distribution['high'] == 1
        assert distribution['medium'] == 1
        assert distribution['low'] == 1
        assert sum(distribution.values()) == len(gaps)
    
    def test_calculate_path_distance_no_context(self):
        """Test path distance calculation without pathway context."""
        content = MagicMock(spec=LearningContent)
        content.tier = 'T2'
        
        distance = self.service._calculate_path_distance(content, None)
        
        assert distance >= 1
        assert isinstance(distance, int)
    
    def test_calculate_path_distance_with_context(self):
        """Test path distance calculation with pathway context."""
        content = MagicMock(spec=LearningContent)
        content.tier = 'T1'  # Early tier
        
        pathway_context = {
            'total_items': 8,  # Large pathway
            'target_persona': 'developer'
        }
        
        distance = self.service._calculate_path_distance(content, pathway_context)
        
        # T1 content in large pathway should have higher distance
        assert distance >= 4
    
    def test_calculate_path_distance_tier_progression(self):
        """Test path distance varies correctly by tier."""
        pathway_context = {'total_items': 5}
        
        content_t1 = MagicMock(spec=LearningContent)
        content_t1.tier = 'T1'
        
        content_t4 = MagicMock(spec=LearningContent)
        content_t4.tier = 'T4'
        
        distance_t1 = self.service._calculate_path_distance(content_t1, pathway_context)
        distance_t4 = self.service._calculate_path_distance(content_t4, pathway_context)
        
        # T1 should be further from end goal than T4
        assert distance_t1 > distance_t4
    
    def test_calculate_pathway_strength_no_gaps(self):
        """Test pathway strength calculation with no gaps."""
        pathway = MagicMock()
        pathway.items = [MagicMock(), MagicMock()]  # 2 items
        
        strength = self.service._calculate_pathway_strength(pathway, [])
        
        assert strength == 1.0  # Perfect strength with no gaps
    
    def test_calculate_pathway_strength_with_gaps(self):
        """Test pathway strength calculation with various gaps."""
        pathway = MagicMock()
        pathway.items = [MagicMock(), MagicMock()]  # 2 items
        
        gaps = [
            ContentGap('missing_prerequisite', 'concept1', 1, 'content1', 0, 0, 'T1', [], []),
            ContentGap('weak_support', 'concept2', 2, 'content2', 1, 30, 'T2', [0.6], [])
        ]
        
        strength = self.service._calculate_pathway_strength(pathway, gaps)
        
        # Should penalize missing prereqs more than weak support
        # Expected: 1.0 - (1*0.8 + 1*0.3) / 2 = 0.45
        assert abs(strength - 0.45) < 0.01
    
    def test_calculate_weighted_gap_score_empty_gaps(self):
        """Test weighted gap score calculation with no gaps."""
        score = self.service._calculate_weighted_gap_score([])
        assert score == 0.0
    
    def test_calculate_weighted_gap_score_single_gap(self):
        """Test weighted gap score calculation with single gap."""
        gap = ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='concept',
            current_content_id=1,
            prerequisite_for='content',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            gap_severity_score=0.8,
            outcome_weight=0.9
        )
        
        score = self.service._calculate_weighted_gap_score([gap])
        
        # Score should be weighted severity
        expected = (0.8 * 0.9) / 1  # severity * weight / max_possible
        assert abs(score - expected) < 0.01
    
    def test_identify_critical_gaps(self):
        """Test identification of critical gaps."""
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
                outcome_weight=0.8
            ),
            ContentGap(
                gap_type='weak_support',
                missing_concept='minor_concept',
                current_content_id=2,
                prerequisite_for='content2',
                supporting_content_count=1,
                average_duration=30,
                average_difficulty='T1',
                similarity_scores=[0.5],
                recommendations=[],
                gap_severity_score=0.3,
                outcome_weight=0.4
            )
        ]
        
        critical_gaps = self.service._identify_critical_gaps(gaps)
        
        # Should return concepts sorted by severity * weight
        assert len(critical_gaps) <= 5
        assert 'critical_concept' in critical_gaps
        assert critical_gaps[0] == 'critical_concept'  # Highest score should be first
    
    def test_calculate_gap_distribution(self):
        """Test gap distribution calculation."""
        gaps = [
            ContentGap(
                gap_type='missing_prerequisite',
                missing_concept='critical',
                current_content_id=1,
                prerequisite_for='content1',
                supporting_content_count=0,
                average_duration=0,
                average_difficulty='unknown',
                similarity_scores=[],
                recommendations=[],
                gap_severity_score=0.9  # Critical
            ),
            ContentGap(
                gap_type='weak_support',
                missing_concept='low',
                current_content_id=4,
                prerequisite_for='content4',
                supporting_content_count=2,
                average_duration=45,
                average_difficulty='T2',
                similarity_scores=[0.8, 0.9],
                recommendations=[],
                gap_severity_score=0.2  # Low
            )
        ]
        
        distribution = self.service._calculate_gap_distribution(gaps)
        
        assert distribution['critical'] == 1
        assert distribution['low'] == 1
        assert sum(distribution.values()) == len(gaps)
    
    def test_calculate_domain_strength_empty_content(self):
        """Test domain strength calculation with no content."""
        strength = self.service._calculate_domain_strength([], [])
        assert strength == 0.0
    
    def test_calculate_domain_strength_with_gaps(self):
        """Test domain strength calculation with gaps."""
        content_items = [MagicMock(), MagicMock(), MagicMock()]  # 3 items
        
        gaps = [
            ContentGap('missing_prerequisite', 'concept1', 1, 'content1', 0, 0, 'T1', [], []),
            ContentGap('weak_support', 'concept2', 2, 'content2', 1, 30, 'T2', [0.6], [])
        ]
        
        strength = self.service._calculate_domain_strength(content_items, gaps)
        
        # Domain should be less penalized than pathway
        # Expected: 1.0 - (1*0.7 + 1*0.4) / 3 ≈ 0.63
        expected = 1.0 - (1*0.7 + 1*0.4) / 3
        assert abs(strength - expected) < 0.01
    
    def test_calculate_average_difficulty_empty(self):
        """Test average difficulty calculation with empty content."""
        avg_difficulty = self.service._calculate_average_difficulty([])
        assert avg_difficulty == 'unknown'
    
    def test_calculate_average_difficulty_single_tier(self):
        """Test average difficulty calculation with single tier."""
        supporting_content = [{'tier': 'T2'}]
        avg_difficulty = self.service._calculate_average_difficulty(supporting_content)
        assert avg_difficulty == 'T2'
    
    def test_calculate_average_difficulty_mixed_tiers(self):
        """Test average difficulty calculation with mixed tiers."""
        supporting_content = [
            {'tier': 'T1'},  # 1
            {'tier': 'T2'},  # 2
            {'tier': 'T3'}   # 3
        ]
        # Average = (1+2+3)/3 = 2.0 -> T2
        avg_difficulty = self.service._calculate_average_difficulty(supporting_content)
        assert avg_difficulty == 'T2'
    
    def test_calculate_average_difficulty_boundary_cases(self):
        """Test average difficulty calculation at tier boundaries."""
        # Test T1/T2 boundary (1.5)
        supporting_content = [{'tier': 'T1'}, {'tier': 'T2'}]  # avg = 1.5
        avg_difficulty = self.service._calculate_average_difficulty(supporting_content)
        assert avg_difficulty == 'T1'  # <= 1.5 maps to T1
        
        # Test T3/T4 boundary (3.5)
        supporting_content = [{'tier': 'T3'}, {'tier': 'T4'}]  # avg = 3.5
        avg_difficulty = self.service._calculate_average_difficulty(supporting_content)
        assert avg_difficulty == 'T3'  # <= 3.5 maps to T3
    
    def test_outcome_weight_bounds(self):
        """Test outcome weight is always bounded between 0 and 1."""
        # Test extreme values
        gap_extreme = ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='concept',
            current_content_id=1,
            prerequisite_for='content',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            dependency_depth=100,  # Extreme value
            path_distance=0        # Extreme value
        )
        
        weight = self.service._calculate_outcome_weight(gap_extreme)
        assert 0.0 <= weight <= 1.0
    
    def test_gap_severity_bounds(self):
        """Test gap severity is always bounded between 0 and 1."""
        # Test with extreme similarity scores
        gap_extreme = ContentGap(
            gap_type='weak_support',
            missing_concept='concept',
            current_content_id=1,
            prerequisite_for='content',
            supporting_content_count=1,
            average_duration=30,
            average_difficulty='T1',
            similarity_scores=[0.0, 0.0, 0.0],  # Very poor similarity
            recommendations=[],
            outcome_weight=2.0  # Extreme weight
        )
        
        severity = self.service._calculate_gap_severity(gap_extreme)
        assert 0.0 <= severity <= 1.0
    
    def test_outcome_weight_bounds(self):
        """Test outcome weight is always bounded between 0 and 1."""
        # Test extreme values
        gap_extreme = ContentGap(
            gap_type='missing_prerequisite',
            missing_concept='concept',
            current_content_id=1,
            prerequisite_for='content',
            supporting_content_count=0,
            average_duration=0,
            average_difficulty='unknown',
            similarity_scores=[],
            recommendations=[],
            dependency_depth=100,  # Extreme value
            path_distance=0        # Extreme value
        )
        
        weight = self.service._calculate_outcome_weight(gap_extreme)
        assert 0.0 <= weight <= 1.0
    
    def test_gap_severity_bounds(self):
        """Test gap severity is always bounded between 0 and 1."""
        # Test with extreme similarity scores
        gap_extreme = ContentGap(
            gap_type='weak_support',
            missing_concept='concept',
            current_content_id=1,
            prerequisite_for='content',
            supporting_content_count=1,
            average_duration=30,
            average_difficulty='T1',
            similarity_scores=[0.0, 0.0, 0.0],  # Very poor similarity
            recommendations=[],
            outcome_weight=2.0  # Extreme weight
        )
        
        severity = self.service._calculate_gap_severity(gap_extreme)
        assert 0.0 <= severity <= 1.0