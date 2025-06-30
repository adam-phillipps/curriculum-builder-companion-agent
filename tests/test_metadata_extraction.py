"""Tests for metadata extraction functionality."""
import pytest
from src.agents.tools import _extract_from_text

class TestMetadataExtraction:
    """Test metadata extraction from content."""
    
    def test_extract_from_text_basic(self):
        """Test basic text extraction."""
        content = "Learn AWS Lambda basics with Python"
        result = _extract_from_text(content, None, "T2", ["developer"], "lesson", [], None, None)
        
        assert result["tier"] == "T2"
        assert result["personas"] == ["developer"]
        assert result["content_type"] == "lesson"
        assert result["title"] == "Learning Content"
        assert "Lambda" in result["aws_services"]
    
    def test_extract_aws_services(self):
        """Test AWS service detection."""
        content = "Use S3 for storage, Lambda for compute, and EC2 for servers"
        result = _extract_from_text(content, None, "T2", ["developer"], "lesson", [], None, None)
        
        assert "S3" in result["aws_services"]
        assert "Lambda" in result["aws_services"]
        assert "EC2" in result["aws_services"]
    
    def test_duration_estimation(self):
        """Test duration estimation based on content length."""
        short_content = "Short lesson"
        long_content = " ".join(["word"] * 200)  # 200 words
        
        short_result = _extract_from_text(short_content, None, "T1", ["developer"], "lesson", [], None, None)
        long_result = _extract_from_text(long_content, None, "T1", ["developer"], "lesson", [], None, None)
        
        assert short_result["estimated_duration"] == 30  # Minimum
        assert long_result["estimated_duration"] > short_result["estimated_duration"]
        assert long_result["estimated_duration"] <= 180  # Maximum
    
    def test_fallback_values(self):
        """Test fallback values when suggestions are None."""
        content = "Basic content"
        result = _extract_from_text(content, None, None, None, None, [], None, None)
        
        assert result["tier"] == "T2"  # Default
        assert result["personas"] == ["developer"]  # Default
        assert result["content_type"] == "lesson"  # Default
        assert result["estimated_cost"] == 5.0
    
    def test_description_truncation(self):
        """Test description truncation for long content."""
        long_content = "a" * 300  # 300 characters
        result = _extract_from_text(long_content, None, "T1", ["developer"], "lesson", [], None, None)
        
        assert len(result["description"]) <= 203  # 200 + "..."
        assert result["description"].endswith("...")
    
    def test_technical_requirements(self):
        """Test technical requirements are set."""
        content = "Python tutorial"
        result = _extract_from_text(content, None, "T2", ["developer"], "lesson", [], None, None)
        
        assert "runtime" in result["technical_requirements"]
        assert result["technical_requirements"]["runtime"] == "python3.9"