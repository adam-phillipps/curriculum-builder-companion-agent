"""
Unit tests for pathway generation functionality.
"""
import pytest
from src.api.routes.pathway import calculate_domain_similarity


class TestDomainSimilarity:
    """Test domain similarity calculation."""
    
    def test_exact_domain_match(self):
        """Test exact domain match returns 1.0."""
        node1 = {"domain_tags": ["ml_engineer", "T2"]}
        node2 = {"domain_tags": ["ml_engineer", "T3"]}
        
        similarity = calculate_domain_similarity(node1, node2)
        assert similarity == 1.0
    
    def test_related_domains(self):
        """Test related domains return 0.6."""
        node1 = {"domain_tags": ["ml_engineer"]}
        node2 = {"domain_tags": ["architect"]}
        
        similarity = calculate_domain_similarity(node1, node2)
        assert similarity == 0.6
    
    def test_distant_domains(self):
        """Test distant domains return 0.2."""
        node1 = {"domain_tags": ["ml_engineer"]}
        node2 = {"domain_tags": ["law"]}
        
        similarity = calculate_domain_similarity(node1, node2)
        assert similarity == 0.2
    
    def test_empty_tags(self):
        """Test empty tags return minimal similarity."""
        node1 = {"domain_tags": []}
        node2 = {"domain_tags": ["ml_engineer"]}
        
        similarity = calculate_domain_similarity(node1, node2)
        assert similarity == 0.1
    
    def test_cross_domain_bridging(self):
        """Test cross-domain bridging scenarios."""
        law_node = {"domain_tags": ["law"]}
        research_node = {"domain_tags": ["research"]}
        data_node = {"domain_tags": ["data_science"]}
        
        # Law -> Research should be related (0.6)
        assert calculate_domain_similarity(law_node, research_node) == 0.6
        
        # Research -> Data Science should be related (0.6)  
        assert calculate_domain_similarity(research_node, data_node) == 0.6
        
        # Law -> Data Science should be distant (0.2)
        assert calculate_domain_similarity(law_node, data_node) == 0.2
    
    def test_ml_engineering_relationships(self):
        """Test ML engineering domain relationships."""
        ml_node = {"domain_tags": ["ml_engineer"]}
        arch_node = {"domain_tags": ["architect"]}
        dev_node = {"domain_tags": ["developer"]}
        
        # All should be related
        assert calculate_domain_similarity(ml_node, arch_node) == 0.6
        assert calculate_domain_similarity(ml_node, dev_node) == 0.6
        assert calculate_domain_similarity(arch_node, dev_node) == 0.6
    
    def test_multiple_tags_intersection(self):
        """Test nodes with multiple tags find intersections."""
        node1 = {"domain_tags": ["T2", "ml_engineer", "python"]}
        node2 = {"domain_tags": ["T3", "architect", "python"]}
        
        # Should find intersection on "python" and return 1.0
        similarity = calculate_domain_similarity(node1, node2)
        assert similarity == 1.0
    
    def test_no_tags_both_nodes(self):
        """Test both nodes with no tags."""
        node1 = {"domain_tags": []}
        node2 = {"domain_tags": []}
        
        similarity = calculate_domain_similarity(node1, node2)
        assert similarity == 0.1
    
    def test_missing_domain_tags_key(self):
        """Test nodes missing domain_tags key."""
        node1 = {}
        node2 = {"domain_tags": ["ml_engineer"]}
        
        similarity = calculate_domain_similarity(node1, node2)
        assert similarity == 0.1