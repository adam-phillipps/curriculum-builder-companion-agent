"""Tests for configuration and constants."""
import pytest
from src.config import BuilderConstants

class TestBuilderConstants:
    """Test builder constants and enums."""
    
    def test_tiers_constants(self):
        """Test tier constants."""
        tiers = BuilderConstants.TIERS.get_names()
        
        assert "T1" in tiers
        assert "T2" in tiers
        assert "T3" in tiers
        assert "T4" in tiers
        assert len(tiers) == 4
        
        # Test tier info
        assert BuilderConstants.TIERS.T1.name == "T1"
        assert BuilderConstants.TIERS.T1.description == "Foundational"
        assert BuilderConstants.TIERS.T1.min_experience_months == 0
        
        assert BuilderConstants.TIERS.T4.min_experience_months == 24
    
    def test_content_types_constants(self):
        """Test content type constants."""
        content_types = BuilderConstants.CONTENT_TYPES.get_names()
        
        expected_types = ["lesson", "module", "session", "exercise", "assessment", "experiment"]
        for content_type in expected_types:
            assert content_type in content_types
    
    def test_personas_constants(self):
        """Test persona constants."""
        personas = BuilderConstants.PERSONAS.get_names()
        
        expected_personas = ["developer", "architect", "operations", "security", "data_engineer", "ml_engineer", "all_roles"]
        for persona in expected_personas:
            assert persona in personas
    
    def test_sandbox_types_constants(self):
        """Test sandbox type constants."""
        sandbox_types = BuilderConstants.SANDBOX_TYPES.get_names()
        
        expected_types = ["individual", "shared", "isolated", "managed"]
        for sandbox_type in expected_types:
            assert sandbox_type in sandbox_types
    
    def test_states_constants(self):
        """Test state constants."""
        states = BuilderConstants.STATES.get_names()
        
        expected_states = ["draft", "staged", "in_review", "approved", "rejected", "archived"]
        for state in expected_states:
            assert state in states
        
        # Test state editing permissions
        assert BuilderConstants.STATES.DRAFT.allows_editing is True
        assert BuilderConstants.STATES.APPROVED.allows_editing is False
    
    def test_cost_categories_constants(self):
        """Test cost category constants."""
        categories = BuilderConstants.COST_CATEGORIES.get_names()
        
        expected_categories = ["compute_resources", "storage_resources", "network_resources", "managed_services", "other_resources"]
        for category in expected_categories:
            assert category in categories
    
    def test_review_types_constants(self):
        """Test review type constants."""
        review_types = BuilderConstants.REVIEW_TYPES.get_names()
        
        expected_types = ["technical_review", "editorial_review", "cost_review", "accessibility_review", "ai_review"]
        for review_type in expected_types:
            assert review_type in review_types
        
        # Test required vs optional reviews
        assert BuilderConstants.REVIEW_TYPES.TECHNICAL.required is True
        assert BuilderConstants.REVIEW_TYPES.AI_ASSISTED.required is False
    
    def test_analysis_types_constants(self):
        """Test analysis type constants."""
        analysis_types = BuilderConstants.ANALYSIS_TYPES.get_names()
        
        expected_types = ["coverage_analysis", "gap_analysis", "content_overlap", "cost_analysis", "prerequisite_analysis", "learning_pathway_analysis"]
        for analysis_type in expected_types:
            assert analysis_type in analysis_types
    
    def test_aws_tags_constants(self):
        """Test AWS tags constants."""
        tags = BuilderConstants.AWS_TAGS.get_names()
        
        expected_tags = ["environment", "tier", "role", "lesson", "cost-center", "learner-id"]
        for tag in expected_tags:
            assert tag in tags

class TestConfigValidation:
    """Test configuration validation."""
    
    def test_constants_consistency(self):
        """Test that constants are consistent across the system."""
        # Verify all tier names are valid
        tier_names = BuilderConstants.TIERS.get_names()
        for tier_name in tier_names:
            assert tier_name.startswith("T")
            assert len(tier_name) == 2
        
        # Verify persona names don't have spaces (for code generation)
        persona_names = BuilderConstants.PERSONAS.get_names()
        for persona_name in persona_names:
            assert " " not in persona_name or persona_name == "all_roles"
    
    def test_enum_completeness(self):
        """Test that all enums have get_names() methods."""
        enum_classes = [
            BuilderConstants.TIERS,
            BuilderConstants.CONTENT_TYPES,
            BuilderConstants.PERSONAS,
            BuilderConstants.SANDBOX_TYPES,
            BuilderConstants.STATES,
            BuilderConstants.COST_CATEGORIES,
            BuilderConstants.REVIEW_TYPES,
            BuilderConstants.ANALYSIS_TYPES,
            BuilderConstants.AWS_TAGS
        ]
        
        for enum_class in enum_classes:
            assert hasattr(enum_class, 'get_names')
            names = enum_class.get_names()
            assert isinstance(names, list)
            assert len(names) > 0