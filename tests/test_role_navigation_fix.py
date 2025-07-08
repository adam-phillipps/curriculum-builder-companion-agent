"""
Test cases for role navigation bug fixes.
"""
import pytest
from src.config import BuilderConstants

class TestRoleNavigationFix:
    """Test that role navigation is properly fixed."""
    
    def test_application_roles_available(self):
        """Test that APPLICATION_ROLES are properly defined."""
        roles = BuilderConstants.APPLICATION_ROLES.get_names()
        
        expected_roles = ["learner", "builder", "curriculum_architect", "admin"]
        assert roles == expected_roles
        
        # Ensure no content management role exists
        assert "content_management" not in roles
        assert "content_manager" not in roles
    
    def test_career_roles_separate_from_app_roles(self):
        """Test that career roles are separate from application roles."""
        app_roles = set(BuilderConstants.APPLICATION_ROLES.get_names())
        career_roles = set(BuilderConstants.PERSONAS.get_names())
        
        # Should have no overlap
        overlap = app_roles & career_roles
        assert len(overlap) == 0, f"Found overlap: {overlap}"
        
        # Career roles should include job titles
        assert "developer" in career_roles
        assert "ml_engineer" in career_roles
        
        # App roles should be profile types
        assert "learner" in app_roles
        assert "builder" in app_roles
    
    def test_role_descriptions_appropriate(self):
        """Test that role descriptions are appropriate for their purpose."""
        roles = BuilderConstants.APPLICATION_ROLES
        
        # Profile roles should describe user profiles, not jobs
        assert "profile" in roles.LEARNER.description.lower()
        assert "profile" in roles.BUILDER.description.lower()
        assert "profile" in roles.CURRICULUM_ARCHITECT.description.lower()
        assert "profile" in roles.ADMIN.description.lower()

if __name__ == "__main__":
    pytest.main([__file__])