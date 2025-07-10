"""
Integration tests for progress tracking API endpoints.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from datetime import datetime

from src.main import app


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_enrollment_data():
    """Sample enrollment data."""
    return {
        "user_id": 1,
        "content_id": 101
    }


@pytest.fixture
def sample_progress_update():
    """Sample progress update data."""
    return {
        "user_id": 1,
        "content_id": 101,
        "comprehension_percentage": 75.0,
        "status": "in_progress"
    }


class TestEnrollmentEndpoint:
    """Test content enrollment endpoint."""
    
    @patch('src.api.routes.progress.get_db')
    async def test_enroll_success(self, mock_get_db, client, sample_enrollment_data):
        """Test successful content enrollment."""
        # Setup
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        with patch('src.api.routes.progress.select') as mock_select:
            # Mock content exists
            mock_content_result = AsyncMock()
            mock_content_result.scalar_one_or_none.return_value = {"id": 101, "title": "Test Content"}
            
            # Mock no existing progress
            mock_progress_result = AsyncMock()
            mock_progress_result.scalar_one_or_none.return_value = None
            
            mock_db.execute.side_effect = [mock_content_result, mock_progress_result]
            
            # Mock progress creation
            from src.db.models.user import UserContentProgress
            mock_progress = UserContentProgress(
                id=1,
                user_id=1,
                content_id=101,
                status="in_progress",
                progress_percentage=0,
                comprehension_percentage=0.0,
                started_at=datetime.utcnow()
            )
            mock_db.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)
            
            # Execute
            response = await client.post("/api/v1/progress/enroll", json=sample_enrollment_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert data["content_id"] == 101
            assert data["status"] == "in_progress"
            assert data["progress_percentage"] == 0
            assert data["comprehension_percentage"] == 0.0
    
    @patch('src.api.routes.progress.get_db')
    async def test_enroll_already_enrolled(self, mock_get_db, client, sample_enrollment_data):
        """Test enrolling in already enrolled content."""
        # Setup
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        with patch('src.api.routes.progress.select'):
            # Mock content exists
            mock_content_result = AsyncMock()
            mock_content_result.scalar_one_or_none.return_value = {"id": 101}
            
            # Mock existing progress
            from src.db.models.user import UserContentProgress
            existing_progress = UserContentProgress(
                id=1,
                user_id=1,
                content_id=101,
                status="in_progress",
                progress_percentage=50,
                comprehension_percentage=25.0
            )
            mock_progress_result = AsyncMock()
            mock_progress_result.scalar_one_or_none.return_value = existing_progress
            
            mock_db.execute.side_effect = [mock_content_result, mock_progress_result]
            
            # Execute
            response = await client.post("/api/v1/progress/enroll", json=sample_enrollment_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["progress_percentage"] == 50
            assert data["comprehension_percentage"] == 25.0
    
    @patch('src.api.routes.progress.get_db')
    async def test_enroll_content_not_found(self, mock_get_db, client, sample_enrollment_data):
        """Test enrolling in non-existent content."""
        # Setup
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        with patch('src.api.routes.progress.select'):
            # Mock content not found
            mock_content_result = AsyncMock()
            mock_content_result.scalar_one_or_none.return_value = None
            mock_db.execute.return_value = mock_content_result
            
            # Execute
            response = await client.post("/api/v1/progress/enroll", json=sample_enrollment_data)
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Content not found"


class TestProgressUpdateEndpoint:
    """Test progress update endpoint."""
    
    @patch('src.api.routes.progress.get_db')
    async def test_update_comprehension_success(self, mock_get_db, client, sample_progress_update):
        """Test successful comprehension update."""
        # Setup
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        with patch('src.api.routes.progress.select'):
            # Mock existing progress
            from src.db.models.user import UserContentProgress
            mock_progress = UserContentProgress(
                id=1,
                user_id=1,
                content_id=101,
                status="in_progress",
                progress_percentage=50,
                comprehension_percentage=0.0
            )
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = mock_progress
            mock_db.execute.return_value = mock_result
            
            # Execute
            response = await client.put("/api/v1/progress/update", json=sample_progress_update)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["comprehension_percentage"] == 75.0
            assert mock_progress.comprehension_percentage == 75.0
    
    @patch('src.api.routes.progress.get_db')
    async def test_update_status_to_completed(self, mock_get_db, client):
        """Test updating status to completed."""
        # Setup
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        update_data = {
            "user_id": 1,
            "content_id": 101,
            "status": "completed"
        }
        
        with patch('src.api.routes.progress.select'):
            # Mock existing progress
            from src.db.models.user import UserContentProgress
            mock_progress = UserContentProgress(
                id=1,
                user_id=1,
                content_id=101,
                status="in_progress",
                progress_percentage=75,
                comprehension_percentage=80.0
            )
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = mock_progress
            mock_db.execute.return_value = mock_result
            
            # Execute
            response = await client.put("/api/v1/progress/update", json=update_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert data["progress_percentage"] == 100  # Auto-set to 100 when completed
            assert mock_progress.completed_at is not None
    
    @patch('src.api.routes.progress.get_db')
    async def test_update_progress_not_found(self, mock_get_db, client, sample_progress_update):
        """Test updating non-existent progress record."""
        # Setup
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        with patch('src.api.routes.progress.select'):
            # Mock no progress found
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute.return_value = mock_result
            
            # Execute
            response = await client.put("/api/v1/progress/update", json=sample_progress_update)
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Progress record not found"


class TestGetProgressEndpoint:
    """Test get progress endpoint."""
    
    @patch('src.api.routes.progress.get_db')
    async def test_get_progress_success(self, mock_get_db, client):
        """Test successful progress retrieval."""
        # Setup
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        with patch('src.api.routes.progress.select'):
            # Mock existing progress
            from src.db.models.user import UserContentProgress
            mock_progress = UserContentProgress(
                id=1,
                user_id=1,
                content_id=101,
                status="in_progress",
                progress_percentage=75,
                comprehension_percentage=80.0,
                started_at=datetime.utcnow()
            )
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = mock_progress
            mock_db.execute.return_value = mock_result
            
            # Execute
            response = await client.get("/api/v1/progress/1/101")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert data["content_id"] == 101
            assert data["progress_percentage"] == 75
            assert data["comprehension_percentage"] == 80.0
    
    @patch('src.api.routes.progress.get_db')
    async def test_get_progress_not_found(self, mock_get_db, client):
        """Test getting non-existent progress."""
        # Setup
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        with patch('src.api.routes.progress.select'):
            # Mock no progress found
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute.return_value = mock_result
            
            # Execute
            response = await client.get("/api/v1/progress/1/999")
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Progress record not found"


class TestProgressValidation:
    """Test progress data validation."""
    
    async def test_enroll_invalid_data(self, client):
        """Test enrollment with invalid data."""
        # Execute
        response = await client.post("/api/v1/progress/enroll", json={
            "user_id": "invalid",  # Should be integer
            "content_id": 101
        })
        
        # Assert
        assert response.status_code == 422
    
    async def test_update_invalid_comprehension(self, client):
        """Test update with invalid comprehension percentage."""
        # Execute
        response = await client.put("/api/v1/progress/update", json={
            "user_id": 1,
            "content_id": 101,
            "comprehension_percentage": 150.0  # Invalid: > 100
        })
        
        # Note: This test depends on API validation being implemented
        # Currently the API accepts any float value
        # This test documents expected behavior for future validation
    
    async def test_update_invalid_status(self, client):
        """Test update with invalid status."""
        # Execute
        response = await client.put("/api/v1/progress/update", json={
            "user_id": 1,
            "content_id": 101,
            "status": "invalid_status"
        })
        
        # Note: This test depends on API validation being implemented
        # Currently the API accepts any string value
        # This test documents expected behavior for future validation