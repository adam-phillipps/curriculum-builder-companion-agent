'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { api } from '@/lib/api';

interface PathwayNode {
  id: string;
  content_id: number;
  weight: number;
  completion: number;
  status: string;
  name: string;
  description: string;
}

interface ChainImpact {
  [key: string]: number;
}

interface InteractivePathwayGraphProps {
  userId: number;
  pathwayId: number;
}

export default function InteractivePathwayGraph({ userId, pathwayId }: InteractivePathwayGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [nodes, setNodes] = useState<PathwayNode[]>([]);
  const [chainImpacts, setChainImpacts] = useState<ChainImpact>({});
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    showCompleted: true,
    showInProgress: true,
    showNotStarted: true,
    selectedOutcomes: [] as string[]
  });
  const [availableOutcomes, setAvailableOutcomes] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadPathwayData();
  }, [userId, pathwayId]);

  useEffect(() => {
    if (nodes.length > 0) {
      renderGraph();
    }
  }, [nodes, chainImpacts, hoveredNode, filters]);

  const loadPathwayData = async () => {
    try {
      console.log('Loading pathway data for user:', userId, 'pathway:', pathwayId);
      
      // Use direct fetch to avoid API client issues
      const response = await fetch(`http://localhost:8001/users/${userId}/content-progress`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const userProgress = await response.json();
      
      console.log('User progress data:', userProgress);
      console.log('Progress length:', userProgress?.length);
      
      if (!userProgress || userProgress.length === 0) {
        console.log('No progress data found');
        setNodes([]);
        setChainImpacts({});
        return;
      }
      
      // Get content details to extract learning outcomes
      const contentResponse = await fetch('http://localhost:8001/api/v1/content');
      const allContent = await contentResponse.json();
      
      // Define tree structure with proper prerequisites
      const treeStructure = {
        1: { prereqs: [], outcomes: ['Mathematics Fundamentals'] },
        2: { prereqs: [1], outcomes: ['Mathematics Fundamentals'] },
        3: { prereqs: [], outcomes: ['Programming Fundamentals'] },
        4: { prereqs: [3], outcomes: ['Programming Fundamentals'] },
        5: { prereqs: [2, 4], outcomes: ['ML Theory'] },
        6: { prereqs: [5], outcomes: ['Neural Networks Mastery'] }
      };
      
      // Convert user progress to pathway nodes with tree structure
      const mockNodes = userProgress.map((progress: any) => {
        const contentItem = allContent.find((c: any) => c.id === progress.content_id);
        const treeInfo = treeStructure[progress.content_id as keyof typeof treeStructure];
        const outcomes = treeInfo?.outcomes || contentItem?.learning_objectives || [`Objective ${progress.content_id}`];
        
        return {
          id: `node_${progress.content_id}`,
          content_id: progress.content_id,
          weight: 0.5,
          completion: progress.progress_percentage,
          status: progress.status,
          name: contentItem?.title || `Learning Item ${progress.content_id}`,
          description: `Progress: ${progress.progress_percentage}% - ${progress.time_spent_minutes} minutes`,
          learning_outcomes: outcomes,
          prerequisites: treeInfo?.prereqs || []
        };
      });
      
      // Extract all unique learning outcomes for filter
      const allOutcomes = new Set<string>();
      mockNodes.forEach(node => {
        node.learning_outcomes.forEach((outcome: string) => allOutcomes.add(outcome));
      });
      setAvailableOutcomes(Array.from(allOutcomes));
      
      console.log('Generated nodes:', mockNodes);
      
      setNodes(mockNodes);
      
      // Generate chain impacts based on actual completion
      const impacts: ChainImpact = {};
      mockNodes.forEach(node => {
        impacts[node.id] = (node.completion / 100) * node.weight;
      });
      
      console.log('Generated impacts:', impacts);
      setChainImpacts(impacts);
      
    } catch (error) {
      console.error('Failed to load pathway data:', error);
      setNodes([]);
      setChainImpacts({});
    }
  };

  const getNodeRadius = (node: PathwayNode, isHovered: boolean = false) => {
    const baseRadius = 25;
    const importance = chainImpacts[node.id] || 0.5;
    const impactMultiplier = isHovered ? importance * 40 : importance * 25;
    return Math.max(baseRadius, baseRadius + impactMultiplier);
  };

  const getNodeColor = (node: PathwayNode) => {
    const colors = {
      completed: '#10B981',
      in_progress: '#F59E0B', 
      not_started: '#6B7280'
    };
    return colors[node.status as keyof typeof colors] || '#6B7280';
  };

  const getFilteredNodes = () => {
    return nodes.filter(node => {
      if (!filters.showCompleted && node.status === 'completed') return false;
      if (!filters.showInProgress && node.status === 'in_progress') return false;
      if (!filters.showNotStarted && node.status === 'not_started') return false;
      
      const importance = chainImpacts[node.id] || 0;
      if (importance < filters.minImpact) return false;
      
      if (filters.showHighImpact && importance < 0.7) return false;
      
      // Filter by selected learning outcomes
      if (filters.selectedOutcomes.length > 0) {
        const hasSelectedOutcome = node.learning_outcomes?.some((outcome: string) => 
          filters.selectedOutcomes.includes(outcome)
        );
        if (!hasSelectedOutcome) return false;
      }
      
      return true;
    });
  };

  const renderGraph = () => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 600;
    const filteredNodes = getFilteredNodes();
    
    console.log('Rendering graph with nodes:', filteredNodes.length);
    console.log('Filtered nodes:', filteredNodes);

    if (filteredNodes.length === 0) {
      // Show "no data" message
      svg.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('font-size', '16px')
        .attr('fill', '#666')
        .text('No learning data available');
      return;
    }

    // Create prerequisite-based directed links (prerequisite -> dependent)
    const links = [];
    filteredNodes.forEach(node => {
      // Create links from prerequisites to this node
      if (node.prerequisites && node.prerequisites.length > 0) {
        node.prerequisites.forEach((prereqId: number) => {
          const prereqNode = filteredNodes.find(n => n.content_id === prereqId);
          if (prereqNode) {
            links.push({
              source: prereqNode.id,
              target: node.id,
              weight: 0.8
            });
          }
        });
      }
    });
    
    console.log('Generated links:', links.length);

    // Force simulation with horizontal tree layout (root on left)
    const simulation = d3.forceSimulation(filteredNodes as any)
      .force('link', d3.forceLink(links).id((d: any) => d.id).strength(0.5).distance(120))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('x', d3.forceX().x((d: any) => {
        // Position nodes horizontally: leaves on right, root on left
        const depth = getNodeDepth(d, filteredNodes, links);
        return 100 + (depth * 120); // Root nodes on left
      }).strength(0.9))
      .force('y', d3.forceY(height / 2).strength(0.2))
      .force('collision', d3.forceCollide().radius((d: any) => getNodeRadius(d) + 20));

    // Links with arrowheads for direction
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 8)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#94A3B8');
    
    const linkElements = svg.append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#94A3B8')
      .attr('stroke-width', 2)
      .attr('marker-end', 'url(#arrowhead)')
      .attr('opacity', (d: any) => {
        if (!hoveredNode) return 0.3;
        return (d.source.id === hoveredNode || d.target.id === hoveredNode) ? 0.8 : 0.1;
      });

    // Nodes
    const nodeElements = svg.append('g')
      .selectAll('g')
      .data(filteredNodes)
      .enter()
      .append('g')
      .style('cursor', 'pointer');

    // Node circles
    nodeElements.append('circle')
      .attr('r', (d: any) => getNodeRadius(d, d.id === hoveredNode))
      .attr('fill', (d: any) => getNodeColor(d))
      .attr('stroke', '#E5E7EB')
      .attr('stroke-width', 2)
      .attr('opacity', (d: any) => {
        if (!hoveredNode) return 0.5;
        return d.id === hoveredNode ? 1.0 : 0.3;
      });

    // Node labels (completion % only)
    nodeElements.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.3em')
      .attr('font-size', '11px')
      .attr('font-weight', 'bold')
      .attr('fill', 'white')
      .text((d: any) => `${Math.round(d.completion)}%`);

    // Hover interactions
    nodeElements
      .on('mouseenter', (event, d: any) => {
        setHoveredNode(d.id);
        showTooltip(event, d);
      })
      .on('mouseleave', () => {
        setHoveredNode(null);
        hideTooltip();
      });

    // Update on tick
    simulation.on('tick', () => {
      linkElements
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      nodeElements
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });
  };

  const showTooltip = (event: MouseEvent, node: PathwayNode) => {
    const importance = chainImpacts[node.id] || 0;
    
    const tooltip = d3.select('body').append('div')
      .attr('class', 'pathway-tooltip')
      .style('position', 'absolute')
      .style('background', 'rgba(0, 0, 0, 0.9)')
      .style('color', 'white')
      .style('padding', '12px')
      .style('border-radius', '6px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('z-index', '1000')
      .style('max-width', '250px');

    tooltip.html(`
      <div><strong>${node.name}</strong></div>
      <div style="margin: 8px 0; padding: 4px 0; border-top: 1px solid #444;">
        <div>Status: <span style="color: ${getNodeColor(node)}">${node.status.replace('_', ' ')}</span></div>
        <div>Progress: ${Math.round(node.completion)}%</div>
        <div>Chain Impact: ${Math.round(importance * 100)}%</div>
        <div>Learning Weight: ${Math.round(node.weight * 100)}%</div>
      </div>
      <div style="font-size: 10px; color: #ccc;">${node.description}</div>
    `)
    .style('left', (event.pageX + 15) + 'px')
    .style('top', (event.pageY - 10) + 'px');
  };

  const hideTooltip = () => {
    d3.selectAll('.pathway-tooltip').remove();
  };

  /**
   * Calculate the depth of a node in the prerequisite tree.
   * 
   * Parameters
   * ----------
   * node : PathwayNode
   *     The node to calculate depth for
   * allNodes : PathwayNode[]
   *     All available nodes
   * links : any[]
   *     All prerequisite links
   * 
   * Returns
   * -------
   * number
   *     Depth level (0 = leaf nodes, higher = closer to root)
   */
  const getNodeDepth = (node: any, allNodes: any[], links: any[]): number => {
    const incomingLinks = links.filter(link => link.target === node.id);
    if (incomingLinks.length === 0) return 0; // Leaf node
    
    const maxParentDepth = Math.max(
      ...incomingLinks.map(link => {
        const parentNode = allNodes.find(n => n.id === link.source);
        return parentNode ? getNodeDepth(parentNode, allNodes, links) : 0;
      })
    );
    
    return maxParentDepth + 1;
  };

  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Learning Pathway Tree</h3>
        
        <div className="flex items-center space-x-4">
          <div className="flex space-x-3 text-sm">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.showCompleted}
                onChange={(e) => setFilters({...filters, showCompleted: e.target.checked})}
                className="mr-1"
              />
              Completed
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.showInProgress}
                onChange={(e) => setFilters({...filters, showInProgress: e.target.checked})}
                className="mr-1"
              />
              In Progress
            </label>
          </div>
          
          <div className="relative">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200"
            >
              Learning Outcomes ({filters.selectedOutcomes.length})
            </button>
            
            {showFilters && (
              <div className="absolute top-8 left-0 bg-white border rounded-lg shadow-lg p-4 z-10 min-w-64">
                <h4 className="font-medium mb-2">Filter by Learning Outcomes</h4>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {availableOutcomes.map(outcome => (
                    <label key={outcome} className="flex items-center text-sm">
                      <input
                        type="checkbox"
                        checked={filters.selectedOutcomes.includes(outcome)}
                        onChange={(e) => {
                          const newOutcomes = e.target.checked
                            ? [...filters.selectedOutcomes, outcome]
                            : filters.selectedOutcomes.filter(o => o !== outcome);
                          setFilters({...filters, selectedOutcomes: newOutcomes});
                        }}
                        className="mr-2"
                      />
                      {outcome}
                    </label>
                  ))}
                </div>
                <button
                  onClick={() => setShowFilters(false)}
                  className="mt-2 px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                >
                  Close
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <svg
        ref={svgRef}
        width="800"
        height="600"
        className="border rounded-lg bg-gray-50"
      />

      <div className="mt-4 text-xs text-gray-600 space-y-1">
        <p><strong>Tree Structure:</strong> Learning pathway flows from foundational concepts (right) to final goal (left).</p>
        <p><strong>Prerequisites:</strong> Arrows show prerequisite → dependent relationships.</p>
        <p><strong>Interaction:</strong> Hover nodes to see details and connections.</p>
      </div>
    </div>
  );
}