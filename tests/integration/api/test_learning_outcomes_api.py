"""
Integration tests for learning outcomes API endpoints.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from src.main import app


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_outcome_data():
    """Sample learning outcome data."""
    return {
        "name": "Python Programming Mastery",
        "description": "Master Python programming from basics to advanced",
        "domain": "programming",
        "difficulty_level": "intermediate",
        "tags": ["python", "programming", "development"],
        "created_by_user_id": 1
    }


class TestLearningOutcomesSearch:
    """Test learning outcomes search endpoint."""
    
    @patch('src.api.routes.learning_outcomes.search_similar_outcomes')
    async def test_search_outcomes_success(self, mock_search, client):
        """Test successful outcomes search."""
        # Setup
        mock_search.return_value = [
            {
                "outcome_id": 1,
                "name": "Python Programming",
                "description": "Learn Python basics",
                "domain": "programming",
                "difficulty_level": "beginner",
                "tags": ["python"],
                "similarity_score": 0.85
            }
        ]
        
        # Execute
        response = await client.get("/api/v1/learning-outcomes/search?query=python&max_results=5")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # 1 similar + 1 custom option
        assert data[0]["is_existing"] is True
        assert data[0]["similarity_score"] == 0.85
        assert data[1]["is_existing"] is False  # Custom option
    
    @patch('src.api.routes.learning_outcomes.search_similar_outcomes')
    async def test_search_outcomes_with_domain_filter(self, mock_search, client):
        """Test outcomes search with domain filter."""
        # Setup
        mock_search.return_value = []
        
        # Execute
        response = await client.get("/api/v1/learning-outcomes/search?query=programming&domain=web_development")
        
        # Assert
        assert response.status_code == 200
        mock_search.assert_called_once_with(
            query_text="programming",
            max_results=10,
            domain_filter="web_development"
        )
    
    async def test_search_outcomes_missing_query(self, client):
        """Test search without query parameter."""
        # Execute
        response = await client.get("/api/v1/learning-outcomes/search")
        
        # Assert
        assert response.status_code == 422  # Validation error


class TestCreateLearningOutcome:
    """Test learning outcome creation endpoint."""
    
    @patch('src.api.routes.learning_outcomes.create_learning_outcome')
    async def test_create_outcome_success(self, mock_create, client, sample_outcome_data):
        """Test successful outcome creation."""
        # Setup
        from src.db.models.learning_outcomes import LearningOutcome
        mock_outcome = LearningOutcome(id=1, **sample_outcome_data, status="pending_approval")
        mock_create.return_value = mock_outcome
        
        # Execute
        response = await client.post("/api/v1/learning-outcomes/", json=sample_outcome_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == sample_outcome_data["name"]
        assert data["status"] == "pending_approval"  # User-created outcomes need approval
    
    @patch('src.api.routes.learning_outcomes.create_learning_outcome')
    async def test_create_outcome_admin_approved(self, mock_create, client, sample_outcome_data):
        """Test outcome creation without user ID (admin created)."""
        # Setup
        from src.db.models.learning_outcomes import LearningOutcome
        outcome_data = {**sample_outcome_data}
        del outcome_data["created_by_user_id"]  # Admin creation
        mock_outcome = LearningOutcome(id=1, **outcome_data, status="approved")
        mock_create.return_value = mock_outcome
        
        # Execute
        response = await client.post("/api/v1/learning-outcomes/", json=outcome_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"  # Admin-created outcomes auto-approved
    
    async def test_create_outcome_invalid_data(self, client):
        """Test outcome creation with invalid data."""
        # Execute
        response = await client.post("/api/v1/learning-outcomes/", json={
            "name": "",  # Empty name
            "domain": "programming"
            # Missing required fields
        })
        
        # Assert
        assert response.status_code == 422


class TestListLearningOutcomes:
    """Test learning outcomes listing endpoint."""
    
    @patch('src.api.routes.learning_outcomes.get_learning_outcomes')
    async def test_list_outcomes_success(self, mock_get, client, sample_outcome_data):
        """Test successful outcomes listing."""
        # Setup
        from src.db.models.learning_outcomes import LearningOutcome
        mock_outcomes = [
            LearningOutcome(id=1, **sample_outcome_data),
            LearningOutcome(id=2, **sample_outcome_data, name="Java Programming")
        ]
        mock_get.return_value = mock_outcomes
        
        # Execute
        response = await client.get("/api/v1/learning-outcomes/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[1]["id"] == 2
    
    @patch('src.api.routes.learning_outcomes.get_learning_outcomes')
    async def test_list_outcomes_with_filters(self, mock_get, client):
        """Test outcomes listing with filters."""
        # Setup
        mock_get.return_value = []
        
        # Execute
        response = await client.get("/api/v1/learning-outcomes/?status=approved&domain=programming&skip=0&limit=50")
        
        # Assert
        assert response.status_code == 200
        mock_get.assert_called_once()
        call_args = mock_get.call_args[1]
        assert call_args["status"] == "approved"
        assert call_args["domain"] == "programming"
        assert call_args["skip"] == 0
        assert call_args["limit"] == 50


class TestAdminEndpoints:
    """Test admin-only endpoints."""
    
    @patch('src.api.routes.learning_outcomes.get_learning_outcomes')
    async def test_get_pending_outcomes(self, mock_get, client, sample_outcome_data):
        """Test getting pending outcomes for admin review."""
        # Setup
        from src.db.models.learning_outcomes import LearningOutcome
        mock_outcomes = [
            LearningOutcome(id=1, **sample_outcome_data, status="pending_approval")
        ]
        mock_get.return_value = mock_outcomes
        
        # Execute
        response = await client.get("/api/v1/learning-outcomes/admin/pending")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending_approval"
        mock_get.assert_called_once_with(
            db=mock_get.call_args[0][0],
            status="pending_approval",
            skip=0,
            limit=100
        )
    
    @patch('src.api.routes.learning_outcomes.update_learning_outcome_status')
    async def test_approve_outcome_success(self, mock_update, client, sample_outcome_data):
        """Test successful outcome approval."""
        # Setup
        from src.db.models.learning_outcomes import LearningOutcome
        mock_outcome = LearningOutcome(id=1, **sample_outcome_data, status="approved")
        mock_update.return_value = mock_outcome
        
        # Execute
        response = await client.put("/api/v1/learning-outcomes/admin/1/approve?approve=true")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Outcome approved"
        assert data["outcome_id"] == 1
        mock_update.assert_called_once_with(
            db=mock_update.call_args[0][0],
            outcome_id=1,
            status="approved"
        )
    
    @patch('src.api.routes.learning_outcomes.update_learning_outcome_status')
    async def test_reject_outcome_success(self, mock_update, client, sample_outcome_data):
        """Test successful outcome rejection."""
        # Setup
        from src.db.models.learning_outcomes import LearningOutcome
        mock_outcome = LearningOutcome(id=1, **sample_outcome_data, status="rejected")
        mock_update.return_value = mock_outcome
        
        # Execute
        response = await client.put("/api/v1/learning-outcomes/admin/1/approve?approve=false")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Outcome rejected"
        mock_update.assert_called_once_with(
            db=mock_update.call_args[0][0],
            outcome_id=1,
            status="rejected"
        )
    
    @patch('src.api.routes.learning_outcomes.update_learning_outcome_status')
    async def test_approve_outcome_not_found(self, mock_update, client):
        """Test approving non-existent outcome."""
        # Setup
        mock_update.return_value = None
        
        # Execute
        response = await client.put("/api/v1/learning-outcomes/admin/999/approve")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Learning outcome not found"


class TestDatabaseIntegration:
    """Test database integration with optimized search."""
    
    @patch('src.api.routes.learning_outcomes.search_similar_outcomes')
    async def test_search_with_database_fallback(self, mock_vector_search, client):
        """Test search using database text search with vector fallback."""
        # Setup - simulate database search finding results
        mock_vector_search.return_value = []  # No vector results
        
        with patch('src.api.routes.learning_outcomes.select') as mock_select:
            # Execute
            response = await client.get("/api/v1/learning-outcomes/search?query=python")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            # Should always have at least the custom option
            assert len(data) >= 1
            assert data[-1]["is_existing"] is False  # Custom option at end


class TestPostgreSQLJSONTagsBugFixes:
    """Test fixes for PostgreSQL JSON tags column issues."""
    
    async def test_search_handles_json_tags_column_gracefully(self, client):
        """Test that search handles PostgreSQL JSON tags column without array_to_string errors."""
        from sqlalchemy.exc import ProgrammingError
        from sqlalchemy.dialects.postgresql.asyncpg import ProgrammingError as AsyncPGError
        
        # Mock database error that occurred in production
        with patch('src.api.dependencies.get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Simulate the exact PostgreSQL error from production logs
            pg_error = AsyncPGError(
                "function array_to_string(json, character varying) does not exist",
                None, None
            )
            mock_db.execute.side_effect = ProgrammingError("", "", pg_error)
            
            # Mock vector search fallback
            with patch('src.api.routes.learning_outcomes.search_similar_outcomes') as mock_vector:
                mock_vector.return_value = []
                
                # Execute - should not crash
                response = await client.get("/api/v1/learning-outcomes/search?query=Law")
                
                # Assert - should return custom suggestion despite database error
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["name"] == "Law"
                assert data[0]["is_existing"] is False
    
    async def test_search_uses_json_astext_for_tags_search(self, client):
        """Test that search uses JSON .astext instead of array_to_string for tags."""
        # This test verifies the fix is in place by checking the query structure
        with patch('src.api.dependencies.get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Mock successful query execution
            mock_result = AsyncMock()
            mock_result.scalars.return_value.all.return_value = []
            mock_db.execute.return_value = mock_result
            
            # Execute search
            response = await client.get("/api/v1/learning-outcomes/search?query=python")
            
            # Assert - should execute without PostgreSQL function errors
            assert response.status_code == 200
            mock_db.execute.assert_called_once()
            
            # Verify the query doesn't use array_to_string
            call_args = mock_db.execute.call_args[0][0]
            query_str = str(call_args)
            assert "array_to_string" not in query_str.lower()
    
    async def test_search_handles_cache_permission_errors(self, client):
        """Test that search handles ML library cache permission errors gracefully."""
        with patch('src.api.dependencies.get_db') as mock_get_db:
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db
            
            # Mock successful database query
            mock_result = AsyncMock()
            mock_result.scalars.return_value.all.return_value = []
            mock_db.execute.return_value = mock_result
            
            # Mock vector search with cache permission error
            with patch('src.api.routes.learning_outcomes.search_similar_outcomes') as mock_vector:
                mock_vector.side_effect = PermissionError("[Errno 13] Permission denied: '/home/appuser/.cache'")
                
                # Execute - should not crash
                response = await client.get("/api/v1/learning-outcomes/search?query=test")
                
                # Assert - should return custom suggestion despite cache error
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["name"] == "test"
                assert data[0]["is_existing"] is False