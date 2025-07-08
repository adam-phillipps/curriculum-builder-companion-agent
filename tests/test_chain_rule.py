"""
Test cases for chain rule calculator functionality.
"""
import pytest
from src.utils.chain_rule import ChainRuleCalculator, ChainNode, ChainLink, calculate_learning_impact

class TestChainRuleCalculator:
    """Test the chain rule calculator for learning impact analysis."""
    
    def setup_method(self):
        """Set up test data for each test."""
        self.calculator = ChainRuleCalculator()
        
        # Create test nodes
        self.nodes = [
            ChainNode("node_a", "Fundamentals", 0.6, 0.9, []),
            ChainNode("node_b", "Intermediate", 0.8, 0.7, ["node_a"]),
            ChainNode("node_c", "Advanced", 1.0, 0.2, ["node_b"])
        ]
        
        for node in self.nodes:
            self.calculator.add_node(node)
        
        # Create test links
        self.links = [
            ChainLink("node_a", "node_b", 0.8),
            ChainLink("node_b", "node_c", 0.9),
            ChainLink("node_a", "node_c", 0.3)  # Indirect connection
        ]
        
        for link in self.links:
            self.calculator.add_link(link)
    
    def test_direct_impact_calculation(self):
        """Test direct impact between connected nodes."""
        impact = self.calculator.calculate_chain_impact("node_a", "node_b")
        assert impact == 0.8, f"Expected 0.8, got {impact}"
    
    def test_indirect_impact_calculation(self):
        """Test chain rule for indirect connections."""
        impact = self.calculator.calculate_chain_impact("node_a", "node_c")
        # Should be direct (0.3) + indirect (0.8 * 0.9 * 0.5) = 0.66
        assert impact > 0.3, f"Chain impact should be greater than direct impact"
        assert impact <= 1.0, f"Impact should not exceed 1.0"
    
    def test_self_impact(self):
        """Test that self-impact returns 1.0."""
        impact = self.calculator.calculate_chain_impact("node_a", "node_a")
        assert impact == 1.0
    
    def test_node_importance_calculation(self):
        """Test node importance scoring."""
        importance_a = self.calculator.get_node_importance("node_a")
        importance_c = self.calculator.get_node_importance("node_c")
        
        # Node A should have higher importance (affects more nodes)
        assert importance_a > importance_c
        assert 0 <= importance_a <= 1.0
        assert 0 <= importance_c <= 1.0
    
    def test_critical_path_analysis(self):
        """Test critical path identification."""
        critical_path = self.calculator.get_critical_path("node_c")
        
        assert len(critical_path) > 0
        # Should include node_b as it's a direct prerequisite
        node_ids = [node_id for node_id, _ in critical_path]
        assert "node_b" in node_ids
    
    def test_completion_impact_simulation(self):
        """Test completion impact simulation."""
        impact_changes = self.calculator.simulate_completion_impact("node_a", 1.0)
        
        # Should show positive impact on dependent nodes
        assert len(impact_changes) > 0
        for node_id, change in impact_changes.items():
            assert isinstance(change, float)

class TestLearningImpactCalculation:
    """Test the learning impact calculation function."""
    
    def test_pathway_data_processing(self):
        """Test processing of pathway data."""
        pathway_data = {
            'nodes': [
                {'id': 'content_1', 'content_id': 1, 'weight': 0.6, 'completion': 90, 'prerequisites': []},
                {'id': 'content_2', 'content_id': 2, 'weight': 0.8, 'completion': 75, 'prerequisites': [1]},
                {'id': 'content_3', 'content_id': 3, 'weight': 1.0, 'completion': 0, 'prerequisites': [2]}
            ]
        }
        
        result = calculate_learning_impact(pathway_data)
        
        assert 'chain_impacts' in result
        assert 'node_importance' in result
        assert 'critical_paths' in result
        
        # Check node importance scores
        importance = result['node_importance']
        assert len(importance) == 3
        for node_id, score in importance.items():
            assert 0 <= score <= 1.0
    
    def test_empty_pathway_handling(self):
        """Test handling of empty pathway data."""
        pathway_data = {'nodes': []}
        
        result = calculate_learning_impact(pathway_data)
        
        assert result['chain_impacts'] == {}
        assert result['node_importance'] == {}
        assert result['critical_paths'] == {}

class TestChainRuleEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_circular_dependencies(self):
        """Test handling of circular dependencies."""
        calculator = ChainRuleCalculator()
        
        # Create circular dependency
        nodes = [
            ChainNode("a", "Node A", 0.5, 0.5, ["c"]),
            ChainNode("b", "Node B", 0.5, 0.5, ["a"]),
            ChainNode("c", "Node C", 0.5, 0.5, ["b"])
        ]
        
        for node in nodes:
            calculator.add_node(node)
        
        links = [
            ChainLink("a", "b", 0.5),
            ChainLink("b", "c", 0.5),
            ChainLink("c", "a", 0.5)
        ]
        
        for link in links:
            calculator.add_link(link)
        
        # Should not cause infinite recursion
        impact = calculator.calculate_chain_impact("a", "c")
        assert 0 <= impact <= 1.0
    
    def test_nonexistent_nodes(self):
        """Test handling of nonexistent nodes."""
        calculator = ChainRuleCalculator()
        
        impact = calculator.calculate_chain_impact("nonexistent", "also_nonexistent")
        assert impact == 0.0
        
        importance = calculator.get_node_importance("nonexistent")
        assert importance == 0.0
    
    def test_single_node_pathway(self):
        """Test pathway with single node."""
        pathway_data = {
            'nodes': [
                {'id': 'content_1', 'content_id': 1, 'weight': 1.0, 'completion': 100, 'prerequisites': []}
            ]
        }
        
        result = calculate_learning_impact(pathway_data)
        
        assert len(result['node_importance']) == 1
        assert result['node_importance']['content_1'] >= 0

if __name__ == "__main__":
    pytest.main([__file__])