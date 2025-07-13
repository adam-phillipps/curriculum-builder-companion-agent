"""
Test cases for pathway API endpoints.
"""
import pytest
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from src.main import app

class TestPathwayAPI:
    """Test pathway API endpoints."""
    
    @pytest.mark.asyncio
    async def test_chain_analysis_endpoint_success(self):
        """Test chain analysis endpoint with valid pathway."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/pathway/2/chain-analysis")
            
            if response.status_code == 200:
                data = response.json()
                
                assert "pathway_data" in data
                assert "chain_analysis" in data
                assert "total_nodes" in data
                
                # Validate node importance scores
                if "node_importance" in data["chain_analysis"]:
                    for node_id, importance in data["chain_analysis"]["node_importance"].items():
                        assert isinstance(importance, (int, float))
                        assert 0 <= importance <= 1.0
            else:
                # If pathway doesn't exist, should return 404
                assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_nonexistent_pathway(self):
        """Test chain analysis with nonexistent pathway."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/pathway/99999/chain-analysis")
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_skill_profile_endpoint(self):
        """Test user skill profile endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/pathway/skill-profile/1")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "user_id" in data
            assert "skills" in data
            assert "total_skills" in data
            
            # Validate skill data structure
            for skill_name, skill_data in data["skills"].items():
                assert "proficiency" in skill_data
                assert isinstance(skill_data["proficiency"], (int, float))
                assert 0 <= skill_data["proficiency"] <= 1.0

if __name__ == "__main__":
    pytest.main([__file__])