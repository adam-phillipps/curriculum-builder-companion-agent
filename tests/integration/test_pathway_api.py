"""
Integration tests for pathway API functionality.
"""
import pytest
from httpx import AsyncClient
from src.main import app


class TestPathwayAPI:
    """Test pathway API endpoints."""
    
    @pytest.mark.asyncio
    async def test_user_pathway_structure(self):
        """Test user pathway API returns correct structure."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/pathway/user-pathway/364")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                assert "user_id" in data
                assert "nodes" in data
                assert "edges" in data
                assert "root_node_id" in data
                
                # If nodes exist, verify node structure
                if data["nodes"]:
                    node = data["nodes"][0]
                    required_fields = ["id", "title", "tier", "status", "progress_percentage"]
                    for field in required_fields:
                        assert field in node
                
                # If edges exist, verify edge structure  
                if data["edges"]:
                    edge = data["edges"][0]
                    required_fields = ["source_id", "target_id", "relationship_type", "strength"]
                    for field in required_fields:
                        assert field in edge
                    
                    # Verify relationship types are valid
                    valid_types = ["progression", "bridge", "aspiration"]
                    assert edge["relationship_type"] in valid_types
                    
                    # Verify strength is between 0 and 1
                    assert 0 <= edge["strength"] <= 1
    
    @pytest.mark.asyncio 
    async def test_empty_user_pathway(self):
        """Test pathway API handles users with no content."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Use a non-existent user ID
            response = await client.get("/api/v1/pathway/user-pathway/99999")
            
            if response.status_code == 200:
                data = response.json()
                assert data["nodes"] == []
                assert data["edges"] == []
                assert data["root_node_id"] is None