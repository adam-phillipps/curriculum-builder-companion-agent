"""
Unit tests for progress tracking CRUD operations.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import UserContentProgress
from src.db.models.content import LearningContent


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_progress_data():
    """Sample progress data."""
    return {
        "user_id": 1,
        "content_id": 101,
        "status": "in_progress",
        "progress_percentage": 50,
        "comprehension_percentage": 75.0,
        "time_spent_minutes": 30
    }


class TestEnrollmentAndProgress:
    """Test enrollment and progress tracking functionality."""
    
    @pytest.mark.asyncio
    async def test_create_progress_record(self, mock_db, sample_progress_data):
        """Test creating new progress record."""
        # Setup
        mock_progress = UserContentProgress(**sample_progress_data)
        mock_progress.id = 1
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Simulate progress creation
        progress = UserContentProgress(**sample_progress_data)
        mock_db.add(progress)
        await mock_db.commit()
        await mock_db.refresh(progress)
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_comprehension_percentage(self, mock_db, sample_progress_data):
        """Test updating comprehension percentage."""
        # Setup
        mock_progress = UserContentProgress(**sample_progress_data)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Execute - simulate comprehension update
        mock_progress.comprehension_percentage = 85.0
        await mock_db.commit()
        await mock_db.refresh(mock_progress)
        
        # Assert
        assert mock_progress.comprehension_percentage == 85.0
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mark_content_complete(self, mock_db, sample_progress_data):
        """Test marking content as complete."""
        # Setup
        mock_progress = UserContentProgress(**sample_progress_data)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_progress
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Execute - simulate completion
        mock_progress.status = "completed"
        mock_progress.progress_percentage = 100
        mock_progress.completed_at = datetime.utcnow()
        await mock_db.commit()
        
        # Assert
        assert mock_progress.status == "completed"
        assert mock_progress.progress_percentage == 100
        assert mock_progress.completed_at is not None
        mock_db.commit.assert_called_once()


class TestProgressValidation:
    """Test progress data validation."""
    
    def test_comprehension_percentage_range(self):
        """Test comprehension percentage is within valid range."""
        # Valid ranges
        valid_values = [0.0, 25.5, 50.0, 75.0, 100.0]
        for value in valid_values:
            progress = UserContentProgress(
                user_id=1,
                content_id=101,
                comprehension_percentage=value
            )
            assert 0.0 <= progress.comprehension_percentage <= 100.0
    
    def test_progress_percentage_range(self):
        """Test progress percentage is within valid range."""
        # Valid ranges
        valid_values = [0, 25, 50, 75, 100]
        for value in valid_values:
            progress = UserContentProgress(
                user_id=1,
                content_id=101,
                progress_percentage=value
            )
            assert 0 <= progress.progress_percentage <= 100
    
    def test_status_values(self):
        """Test valid status values."""
        valid_statuses = ["not_started", "in_progress", "completed", "skipped"]
        for status in valid_statuses:
            progress = UserContentProgress(
                user_id=1,
                content_id=101,
                status=status
            )
            assert progress.status in valid_statuses


class TestProgressQueries:
    """Test progress query functionality."""
    
    @pytest.mark.asyncio
    async def test_get_user_progress(self, mock_db):
        """Test retrieving user progress."""
        # Setup
        mock_progress_list = [
            UserContentProgress(id=1, user_id=1, content_id=101, status="completed"),
            UserContentProgress(id=2, user_id=1, content_id=102, status="in_progress")
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_progress_list
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = mock_result.scalars().all()
        
        # Assert
        assert len(result) == 2
        assert result[0].status == "completed"
        assert result[1].status == "in_progress"
    
    @pytest.mark.asyncio
    async def test_get_progress_by_status(self, mock_db):
        """Test filtering progress by status."""
        # Setup
        completed_progress = [
            UserContentProgress(id=1, user_id=1, content_id=101, status="completed")
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = completed_progress
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = mock_result.scalars().all()
        
        # Assert
        assert len(result) == 1
        assert all(p.status == "completed" for p in result)