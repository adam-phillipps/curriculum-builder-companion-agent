"""Fixed API integration tests."""
import pytest
from httpx import AsyncClient
from src.main import app

class TestAPIIntegration:
    """Test API integration with proper async client handling."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_process_content_endpoint(self, sample_content):
        """Test content processing endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/agents/process-content",
                json=sample_content
            )
            assert response.status_code == 200
            data = response.json()
            assert "workflow_id" in data
            assert "status" in data
            assert data["status"] in ["published", "human_review"]
    
    @pytest.mark.asyncio
    async def test_process_content_validation(self):
        """Test content processing input validation."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test missing required field
            invalid_data = {"suggested_tier": "T2"}
            
            response = await client.post(
                "/api/v1/agents/process-content",
                json=invalid_data
            )
            assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_content_endpoint(self):
        """Test get content endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/content")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

class TestAPIErrorHandling:
    """Test API error handling."""
    
    @pytest.mark.asyncio
    async def test_nonexistent_endpoint(self):
        """Test handling of nonexistent endpoints."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/nonexistent")
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_method_not_allowed(self):
        """Test handling of wrong HTTP methods."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete("/api/v1/agents/process-content")
            assert response.status_code == 405