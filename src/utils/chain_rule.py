"""
Generalized Chain Rule Calculator for Learning Content Impact Analysis.
Calculates weighted impact of each learning item on final outcomes using chain rule principles.
"""
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import math

@dataclass
class ChainNode:
    """Represents a node in the learning chain."""
    id: str
    name: str
    base_weight: float  # Direct impact weight (0-1)
    completion: float   # Completion percentage (0-1)
    dependencies: List[str]  # List of prerequisite node IDs

@dataclass
class ChainLink:
    """Represents a weighted connection between nodes."""
    from_node: str
    to_node: str
    weight: float  # Impact weight (0-1)

class ChainRuleCalculator:
    """Calculates chain rule weights for learning pathway impact analysis."""
    
    def __init__(self):
        self.nodes: Dict[str, ChainNode] = {}
        self.links: List[ChainLink] = []
        self.impact_matrix: Dict[Tuple[str, str], float] = {}
    
    def add_node(self, node: ChainNode) -> None:
        """Add a learning content node to the chain."""
        self.nodes[node.id] = node
    
    def add_link(self, link: ChainLink) -> None:
        """Add a weighted connection between nodes."""
        self.links.append(link)
        self.impact_matrix[(link.from_node, link.to_node)] = link.weight
    
    def calculate_chain_impact(self, source_node: str, target_node: str, visited: set = None) -> float:
        """
        Calculate the chain rule impact of source_node on target_node.
        Uses iterative approach to avoid recursion issues.
        """
        if source_node == target_node:
            return 1.0
        
        if visited is None:
            visited = set()
        
        if source_node in visited:
            return 0.0  # Avoid cycles
        
        visited.add(source_node)
        
        # Direct connection
        direct_impact = self.impact_matrix.get((source_node, target_node), 0.0)
        
        # Simple indirect impact (one hop only to avoid recursion)
        indirect_impact = 0.0
        for intermediate_node in self.nodes:
            if intermediate_node not in visited and intermediate_node != target_node:
                path_to_intermediate = self.impact_matrix.get((source_node, intermediate_node), 0.0)
                intermediate_to_target = self.impact_matrix.get((intermediate_node, target_node), 0.0)
                
                if path_to_intermediate > 0 and intermediate_to_target > 0:
                    indirect_impact += path_to_intermediate * intermediate_to_target * 0.5
        
        visited.remove(source_node)
        
        # Total impact is direct + weighted indirect
        total_impact = direct_impact + indirect_impact
        return min(1.0, total_impact)
    
    def calculate_all_impacts(self) -> Dict[Tuple[str, str], float]:
        """Calculate chain rule impacts between all node pairs."""
        all_impacts = {}
        
        for source_id in self.nodes:
            for target_id in self.nodes:
                if source_id != target_id:
                    impact = self.calculate_chain_impact(source_id, target_id)
                    if impact > 0.01:  # Only store significant impacts
                        all_impacts[(source_id, target_id)] = impact
        
        return all_impacts
    
    def get_node_importance(self, node_id: str) -> float:
        """
        Calculate overall importance of a node based on its impact on all other nodes.
        Higher importance = affects more nodes with higher weights.
        """
        if node_id not in self.nodes:
            return 0.0
        
        total_outgoing_impact = 0.0
        total_incoming_impact = 0.0
        
        for other_node in self.nodes:
            if other_node != node_id:
                # Outgoing impact (how much this node affects others)
                outgoing = self.calculate_chain_impact(node_id, other_node)
                total_outgoing_impact += outgoing
                
                # Incoming impact (how much others affect this node)
                incoming = self.calculate_chain_impact(other_node, node_id)
                total_incoming_impact += incoming
        
        # Importance combines both outgoing influence and incoming dependencies
        importance = (total_outgoing_impact * 0.7) + (total_incoming_impact * 0.3)
        return min(1.0, importance)
    
    def get_critical_path(self, target_node: str) -> List[Tuple[str, float]]:
        """
        Find the most critical learning path to reach target_node.
        Returns list of (node_id, impact_weight) tuples.
        """
        if target_node not in self.nodes:
            return []
        
        # Calculate impact of each node on the target
        node_impacts = []
        for node_id in self.nodes:
            if node_id != target_node:
                impact = self.calculate_chain_impact(node_id, target_node)
                if impact > 0:
                    node_impacts.append((node_id, impact))
        
        # Sort by impact (highest first)
        node_impacts.sort(key=lambda x: x[1], reverse=True)
        
        return node_impacts[:5]  # Return top 5 most critical nodes
    
    def simulate_completion_impact(self, node_id: str, new_completion: float) -> Dict[str, float]:
        """
        Simulate the impact of changing a node's completion on all other nodes.
        Returns dict of {node_id: projected_impact_change}
        """
        if node_id not in self.nodes:
            return {}
        
        original_completion = self.nodes[node_id].completion
        impact_changes = {}
        
        # Temporarily update completion
        self.nodes[node_id].completion = new_completion
        completion_delta = new_completion - original_completion
        
        # Calculate impact on all other nodes
        for other_node in self.nodes:
            if other_node != node_id:
                chain_impact = self.calculate_chain_impact(node_id, other_node)
                # Impact change is proportional to completion change and chain weight
                impact_change = completion_delta * chain_impact
                if abs(impact_change) > 0.01:
                    impact_changes[other_node] = impact_change
        
        # Restore original completion
        self.nodes[node_id].completion = original_completion
        
        return impact_changes

def create_pathway_chain_calculator(pathway_data: Dict[str, Any]) -> ChainRuleCalculator:
    """
    Create a ChainRuleCalculator from pathway data.
    Expected format matches our Sankey JSON structure.
    """
    calculator = ChainRuleCalculator()
    
    # Add nodes
    for node_data in pathway_data.get('nodes', []):
        node = ChainNode(
            id=node_data['id'],
            name=f"Content {node_data['content_id']}",
            base_weight=node_data['weight'],
            completion=node_data['completion'] / 100.0,  # Convert percentage to 0-1
            dependencies=node_data.get('prerequisites', [])
        )
        calculator.add_node(node)
    
    # Add links based on prerequisites and weights
    for node_data in pathway_data.get('nodes', []):
        current_id = node_data['id']
        current_weight = node_data['weight']
        
        # Create links to all other nodes (everything connects to everything)
        for other_node in pathway_data.get('nodes', []):
            other_id = other_node['id']
            if current_id != other_id:
                # Calculate connection weight based on prerequisites and base weights
                if node_data['content_id'] in other_node.get('prerequisites', []):
                    # Direct prerequisite - high weight
                    link_weight = current_weight * 0.9
                else:
                    # Indirect connection - weight based on skill overlap
                    link_weight = current_weight * other_node['weight'] * 0.3
                
                if link_weight > 0.05:  # Only add significant connections
                    link = ChainLink(
                        from_node=current_id,
                        to_node=other_id,
                        weight=link_weight
                    )
                    calculator.add_link(link)
    
    return calculator

# Global utility functions
def calculate_learning_impact(pathway_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate learning impact analysis for a pathway using chain rule."""
    calculator = create_pathway_chain_calculator(pathway_data)
    
    # Calculate all chain rule impacts
    all_impacts = calculator.calculate_all_impacts()
    
    # Calculate node importance scores
    node_importance = {}
    for node_id in calculator.nodes:
        importance = calculator.get_node_importance(node_id)
        node_importance[node_id] = importance
    
    # Find critical paths to final learning goal
    final_nodes = [n for n in pathway_data.get('nodes', []) if n.get('weight', 0) >= 0.9]
    critical_paths = {}
    for final_node in final_nodes:
        path = calculator.get_critical_path(final_node['id'])
        critical_paths[final_node['id']] = path
    
    return {
        'chain_impacts': all_impacts,
        'node_importance': node_importance,
        'critical_paths': critical_paths,
        'calculator': calculator  # For further analysis
    }