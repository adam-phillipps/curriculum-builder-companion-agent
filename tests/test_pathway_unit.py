"""
Unit tests for pathway functionality without database dependencies.
"""
import pytest
from unittest.mock import Mock, patch
from src.utils.chain_rule import ChainRuleCalculator, ChainNode, ChainLink, calculate_learning_impact

class TestPathwayChainRuleUnit:
    """Unit tests for pathway chain rule calculations."""
    
    def test_pathway_data_processing(self):
        """Test processing pathway data into chain rule format."""
        pathway_data = {
            'nodes': [
                {'id': 'content_1', 'content_id': 1, 'weight': 0.6, 'completion': 90, 'prerequisites': []},
                {'id': 'content_2', 'content_id': 2, 'weight': 0.8, 'completion': 75, 'prerequisites': [1]},
                {'id': 'content_3', 'content_id': 3, 'weight': 1.0, 'completion': 0, 'prerequisites': [2]}
            ]
        }
        
        result = calculate_learning_impact(pathway_data)
        
        # Validate structure
        assert 'chain_impacts' in result
        assert 'node_importance' in result
        assert 'critical_paths' in result
        
        # Validate node importance calculations
        importance = result['node_importance']
        assert len(importance) == 3
        
        # Final node should have high importance
        assert importance['content_3'] >= 0.5
        
        # All importance scores should be valid
        for node_id, score in importance.items():
            assert 0 <= score <= 1.0
    
    def test_chain_rule_mathematics(self):
        """Test mathematical correctness of chain rule calculations."""
        calculator = ChainRuleCalculator()
        
        # Create test nodes
        nodes = [
            ChainNode("a", "Node A", 0.8, 1.0, []),
            ChainNode("b", "Node B", 0.6, 0.8, ["a"]),
            ChainNode("c", "Node C", 1.0, 0.0, ["b"])
        ]
        
        for node in nodes:
            calculator.add_node(node)
        
        # Create links
        links = [
            ChainLink("a", "b", 0.7),
            ChainLink("b", "c", 0.9),
            ChainLink("a", "c", 0.2)  # Indirect path
        ]
        
        for link in links:
            calculator.add_link(link)
        
        # Test direct impact
        direct_impact = calculator.calculate_chain_impact("a", "b")
        assert direct_impact >= 0.7  # Should include direct connection
        
        # Test chain rule impact
        chain_impact = calculator.calculate_chain_impact("a", "c")
        assert chain_impact > 0.2  # Should be greater than direct connection
        assert chain_impact <= 1.0  # Should not exceed maximum
    
    def test_node_importance_scoring(self):
        """Test node importance scoring algorithm."""
        calculator = ChainRuleCalculator()
        
        # Create pathway with clear importance hierarchy
        nodes = [
            ChainNode("foundation", "Foundation", 0.5, 1.0, []),
            ChainNode("intermediate", "Intermediate", 0.7, 0.8, ["foundation"]),
            ChainNode("advanced", "Advanced", 1.0, 0.0, ["intermediate"])
        ]
        
        for node in nodes:
            calculator.add_node(node)
        
        links = [
            ChainLink("foundation", "intermediate", 0.8),
            ChainLink("intermediate", "advanced", 0.9),
            ChainLink("foundation", "advanced", 0.3)
        ]
        
        for link in links:
            calculator.add_link(link)
        
        # Calculate importance
        foundation_importance = calculator.get_node_importance("foundation")
        intermediate_importance = calculator.get_node_importance("intermediate")
        advanced_importance = calculator.get_node_importance("advanced")
        
        # Foundation should have high outgoing impact
        assert foundation_importance > 0.3
        
        # Advanced should have high incoming impact
        assert advanced_importance > 0.3
        
        # All scores should be valid
        assert 0 <= foundation_importance <= 1.0
        assert 0 <= intermediate_importance <= 1.0
        assert 0 <= advanced_importance <= 1.0
    
    def test_critical_path_analysis(self):
        """Test critical path identification."""
        calculator = ChainRuleCalculator()
        
        # Create branching pathway
        nodes = [
            ChainNode("start", "Start", 0.3, 1.0, []),
            ChainNode("path1", "Path 1", 0.6, 0.8, ["start"]),
            ChainNode("path2", "Path 2", 0.9, 0.7, ["start"]),
            ChainNode("end", "End", 1.0, 0.0, ["path1", "path2"])
        ]
        
        for node in nodes:
            calculator.add_node(node)
        
        links = [
            ChainLink("start", "path1", 0.5),
            ChainLink("start", "path2", 0.8),  # Stronger path
            ChainLink("path1", "end", 0.6),
            ChainLink("path2", "end", 0.9)     # Critical path
        ]
        
        for link in links:
            calculator.add_link(link)
        
        # Get critical path to end
        critical_path = calculator.get_critical_path("end")
        
        assert len(critical_path) > 0
        
        # Path2 should be more critical than Path1
        path_impacts = {node_id: impact for node_id, impact in critical_path}
        assert path_impacts.get("path2", 0) > path_impacts.get("path1", 0)
    
    def test_completion_impact_simulation(self):
        """Test completion impact simulation."""
        calculator = ChainRuleCalculator()
        
        # Create simple pathway
        nodes = [
            ChainNode("prereq", "Prerequisite", 0.7, 0.5, []),  # 50% complete
            ChainNode("main", "Main Content", 1.0, 0.0, ["prereq"])  # Not started
        ]
        
        for node in nodes:
            calculator.add_node(node)
        
        calculator.add_link(ChainLink("prereq", "main", 0.8))
        
        # Simulate completing prerequisite
        impact_changes = calculator.simulate_completion_impact("prereq", 1.0)
        
        # Should show positive impact on main content
        assert "main" in impact_changes
        assert impact_changes["main"] > 0
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        calculator = ChainRuleCalculator()
        
        # Empty calculator
        assert calculator.calculate_chain_impact("nonexistent", "also_nonexistent") == 0.0
        assert calculator.get_node_importance("nonexistent") == 0.0
        assert calculator.get_critical_path("nonexistent") == []
        
        # Single node
        calculator.add_node(ChainNode("single", "Single", 1.0, 1.0, []))
        assert calculator.calculate_chain_impact("single", "single") == 1.0
        assert calculator.get_node_importance("single") >= 0.0

if __name__ == "__main__":
    pytest.main([__file__])