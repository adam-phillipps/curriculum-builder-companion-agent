"""Tests for API integration and endpoints."""
import pytest
from httpx import AsyncClient

class TestAPIIntegration:
    """Test API endpoints and integration."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_process_content_endpoint(self, client: AsyncClient, sample_content):
        """Test content processing endpoint."""
        response = await client.post(
            "/api/v1/agents/process-content",
            json=sample_content
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "workflow_id" in data
        assert "status" in data
        assert "extracted_metadata" in data
        assert "similar_content" in data
        assert "similarity_score" in data
        assert "human_review_required" in data
        
        # Verify workflow completed
        assert data["status"] in ["published", "human_review", "error"]
    
    @pytest.mark.asyncio
    async def test_process_content_validation(self, client: AsyncClient):
        """Test content processing input validation."""
        # Test missing required field
        invalid_data = {"suggested_tier": "T2"}
        
        response = await client.post(
            "/api/v1/agents/process-content",
            json=invalid_data
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_process_content_with_minimal_data(self, client: AsyncClient):
        """Test content processing with minimal required data."""
        minimal_data = {"content": "Basic AWS tutorial"}
        
        response = await client.post(
            "/api/v1/agents/process-content",
            json=minimal_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "workflow_id" in data
    
    @pytest.mark.asyncio
    async def test_get_content_endpoint(self, client: AsyncClient):
        """Test get content endpoint."""
        response = await client.get("/api/v1/content/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_content_workflow_end_to_end(self, client: AsyncClient):
        """Test complete end-to-end content workflow."""
        # Step 1: Submit content
        content_data = {
            "content": "Learn AWS S3 storage basics. This tutorial covers bucket creation, file uploads, and access policies.",
            "suggested_tier": "T1",
            "suggested_personas": ["developer"],
            "suggested_content_type": "lesson"
        }
        
        response = await client.post(
            "/api/v1/agents/process-content",
            json=content_data
        )
        
        assert response.status_code == 200
        workflow_result = response.json()
        
        # Step 2: Verify workflow completed successfully
        assert workflow_result["status"] in ["published", "human_review"]
        
        # Step 3: If published, verify content was created
        if workflow_result["status"] == "published":
            assert workflow_result["content_id"] is not None
            
            # Step 4: Retrieve the created content
            response = await client.get("/api/v1/content/")
            assert response.status_code == 200
            
            content_list = response.json()
            created_content = next(
                (item for item in content_list if item["id"] == workflow_result["content_id"]),
                None
            )
            assert created_content is not None
            assert created_content["tier"] == "T1"

class TestAPIErrorHandling:
    """Test API error handling."""
    
    @pytest.mark.asyncio
    async def test_invalid_json(self, client: AsyncClient):
        """Test handling of invalid JSON."""
        response = await client.post(
            "/api/v1/agents/process-content",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_nonexistent_endpoint(self, client: AsyncClient):
        """Test handling of nonexistent endpoints."""
        response = await client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_method_not_allowed(self, client: AsyncClient):
        """Test handling of wrong HTTP methods."""
        response = await client.delete("/api/v1/agents/process-content")
        
        assert response.status_code == 405