"""
Test cases for application role system functionality.
"""
import pytest
from src.config import BuilderConstants

class TestApplicationRoles:
    """Test application role constants and validation."""
    
    def test_application_roles_constants(self):
        """Test that APPLICATION_ROLES constants are properly defined."""
        roles = BuilderConstants.APPLICATION_ROLES
        
        assert hasattr(roles, 'LEARNER')
        assert hasattr(roles, 'BUILDER') 
        assert hasattr(roles, 'CURRICULUM_ARCHITECT')
        assert hasattr(roles, 'ADMIN')
        
        assert roles.LEARNER.name == "learner"
        assert roles.BUILDER.name == "builder"
        assert roles.CURRICULUM_ARCHITECT.name == "curriculum_architect"
        assert roles.ADMIN.name == "admin"
    
    def test_application_roles_get_names(self):
        """Test that get_names returns correct role names."""
        role_names = BuilderConstants.APPLICATION_ROLES.get_names()
        
        expected_roles = ["learner", "builder", "curriculum_architect", "admin"]
        assert role_names == expected_roles
        assert len(role_names) == 4
    
    def test_application_roles_descriptions(self):
        """Test that roles have proper descriptions."""
        roles = BuilderConstants.APPLICATION_ROLES
        
        assert "learning" in roles.LEARNER.description.lower()
        assert "content" in roles.BUILDER.description.lower()
        assert "curriculum" in roles.CURRICULUM_ARCHITECT.description.lower()
        assert "admin" in roles.ADMIN.description.lower()
    
    def test_personas_vs_application_roles_separation(self):
        """Test that PERSONAS (career roles) are separate from APPLICATION_ROLES."""
        persona_names = BuilderConstants.PERSONAS.get_names()
        app_role_names = BuilderConstants.APPLICATION_ROLES.get_names()
        
        # Should have no overlap
        overlap = set(persona_names) & set(app_role_names)
        assert len(overlap) == 0, f"Found overlap between personas and app roles: {overlap}"
        
        # Personas should be job-related
        assert "developer" in persona_names
        assert "architect" in persona_names
        
        # App roles should be profile-related
        assert "learner" in app_role_names
        assert "builder" in app_role_names

class TestRoleValidation:
    """Test role validation logic."""
    
    def test_valid_application_roles(self):
        """Test validation of valid application roles."""
        valid_roles = BuilderConstants.APPLICATION_ROLES.get_names()
        
        for role in valid_roles:
            assert role in ["learner", "builder", "curriculum_architect", "admin"]
    
    def test_valid_career_roles(self):
        """Test validation of valid career roles.""" 
        valid_careers = BuilderConstants.PERSONAS.get_names()
        
        expected_careers = ["developer", "architect", "operations", "security", "data_engineer", "ml_engineer", "all_roles"]
        assert valid_careers == expected_careers

if __name__ == "__main__":
    pytest.main([__file__])