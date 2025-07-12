'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { api } from '@/lib/api';
import { buildApiUrl } from '../config/api';

interface PathwayNode {
  id: string;
  content_id: number;
  weight: number;
  completion: number;
  status: string;
  name: string;
  description: string;
  learning_outcomes?: string[];
  prerequisites?: number[];
  domain?: string;
  difficulty_level?: string;
  comprehension_percentage?: number;
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
    selectedOutcomes: [] as string[],
    selectedDomain: '',
    selectedDifficulty: '',
    rootNodeId: null as string | null
  });
  const [layoutMode, setLayoutMode] = useState<'hierarchical' | 'centered'>('hierarchical');
  const [availableDomains, setAvailableDomains] = useState<string[]>([]);
  const [availableDifficulties, setAvailableDifficulties] = useState<string[]>([]);
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
      const response = await fetch(buildApiUrl(`users/${userId}/content-progress`));
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
      const contentResponse = await fetch(buildApiUrl('content'));
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
      
      // Convert user progress to pathway nodes with enhanced metadata
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
          prerequisites: treeInfo?.prereqs || [],
          domain: contentItem?.tier || 'general',
          difficulty_level: contentItem?.tier || 'intermediate',
          comprehension_percentage: progress.comprehension_percentage || 0
        };
      });
      
      // Extract domains and difficulties for filters
      const domains = new Set<string>();
      const difficulties = new Set<string>();
      mockNodes.forEach(node => {
        if (node.domain) domains.add(node.domain);
        if (node.difficulty_level) difficulties.add(node.difficulty_level);
      });
      setAvailableDomains(Array.from(domains));
      setAvailableDifficulties(Array.from(difficulties));
      
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
    let filteredNodes = nodes.filter(node => {
      // Status filters
      if (!filters.showCompleted && node.status === 'completed') return false;
      if (!filters.showInProgress && node.status === 'in_progress') return false;
      if (!filters.showNotStarted && node.status === 'not_started') return false;
      
      // Domain filter
      if (filters.selectedDomain && node.domain !== filters.selectedDomain) return false;
      
      // Difficulty filter
      if (filters.selectedDifficulty && node.difficulty_level !== filters.selectedDifficulty) return false;
      
      // Learning outcomes filter
      if (filters.selectedOutcomes.length > 0) {
        const hasSelectedOutcome = node.learning_outcomes?.some((outcome: string) => 
          filters.selectedOutcomes.includes(outcome)
        );
        if (!hasSelectedOutcome) return false;
      }
      
      return true;
    });
    
    // Root node filtering - show only nodes that lead to the selected root
    if (filters.rootNodeId) {
      const rootNode = filteredNodes.find(n => n.id === filters.rootNodeId);
      if (rootNode) {
        const pathToRoot = getPathToNode(rootNode, filteredNodes);
        filteredNodes = filteredNodes.filter(node => pathToRoot.includes(node.id));
      }
    }
    
    return filteredNodes;
  };
  
  // Get all nodes that lead to a specific target node
  const getPathToNode = (targetNode: PathwayNode, allNodes: PathwayNode[]): string[] => {
    const visited = new Set<string>();
    const path: string[] = [];
    
    const traverse = (node: PathwayNode) => {
      if (visited.has(node.id)) return;
      visited.add(node.id);
      path.push(node.id);
      
      // Add all prerequisite nodes
      if (node.prerequisites) {
        node.prerequisites.forEach(prereqId => {
          const prereqNode = allNodes.find(n => n.content_id === prereqId);
          if (prereqNode) {
            traverse(prereqNode);
          }
        });
      }
    };
    
    traverse(targetNode);
    return path;
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

    // Create force simulation based on layout mode
    let simulation;
    
    if (layoutMode === 'hierarchical') {
      // Hierarchical layout with root at top
      simulation = d3.forceSimulation(filteredNodes as any)
        .force('link', d3.forceLink(links).id((d: any) => d.id).strength(0.5).distance(120))
        .force('charge', d3.forceManyBody().strength(-400))
        .force('x', d3.forceX(width / 2).strength(0.1))
        .force('y', d3.forceY().y((d: any) => {
          const depth = getNodeDepth(d, filteredNodes, links);
          return 80 + (depth * 100); // Root at top, dependencies below
        }).strength(0.8))
        .force('collision', d3.forceCollide().radius((d: any) => getNodeRadius(d) + 20));
    } else {
      // Centered layout with root in middle
      const rootNode = filters.rootNodeId ? filteredNodes.find(n => n.id === filters.rootNodeId) : null;
      
      simulation = d3.forceSimulation(filteredNodes as any)
        .force('link', d3.forceLink(links).id((d: any) => d.id).strength(0.3).distance(150))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius((d: any) => getNodeRadius(d) + 25));
        
      // If there's a root node, pin it to center
      if (rootNode) {
        simulation.force('root', d3.forceRadial(0, width / 2, height / 2).strength((d: any) => 
          d.id === filters.rootNodeId ? 1.0 : 0.1
        ));
      }
    }

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

    // Add zoom and pan behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        svg.select('g.graph-container')
          .attr('transform', event.transform);
      });
    
    svg.call(zoom as any);
    
    // Create container for graph elements
    const graphContainer = svg.append('g').attr('class', 'graph-container');
    
    // Move link and node elements to container
    linkElements.remove();
    nodeElements.remove();
    
    const linkElementsInContainer = graphContainer.append('g')
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
    
    const nodeElementsInContainer = graphContainer.append('g')
      .selectAll('g')
      .data(filteredNodes)
      .enter()
      .append('g')
      .style('cursor', 'pointer');
    
    // Recreate node circles and labels
    nodeElementsInContainer.append('circle')
      .attr('r', (d: any) => getNodeRadius(d, d.id === hoveredNode))
      .attr('fill', (d: any) => getNodeColor(d))
      .attr('stroke', (d: any) => d.id === filters.rootNodeId ? '#DC2626' : '#E5E7EB')
      .attr('stroke-width', (d: any) => d.id === filters.rootNodeId ? 4 : 2)
      .attr('opacity', (d: any) => {
        if (!hoveredNode) return 0.8;
        return d.id === hoveredNode ? 1.0 : 0.4;
      })
      .on('click', (event, d: any) => {
        // Set as new root node
        setFilters(prev => ({
          ...prev,
          rootNodeId: prev.rootNodeId === d.id ? null : d.id
        }));
      });
    
    nodeElementsInContainer.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.3em')
      .attr('font-size', '11px')
      .attr('font-weight', 'bold')
      .attr('fill', 'white')
      .text((d: any) => `${Math.round(d.completion)}%`);
    
    // Hover interactions
    nodeElementsInContainer
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
      linkElementsInContainer
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      nodeElementsInContainer
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
  
  // Cleanup tooltips when component unmounts or user navigates away
  useEffect(() => {
    const cleanup = () => {
      d3.selectAll('.pathway-tooltip').remove();
      setHoveredNode(null);
    };
    
    // Cleanup on page visibility change (tab switch)
    const handleVisibilityChange = () => {
      if (document.hidden) {
        cleanup();
      }
    };
    
    // Cleanup on mouse leave from entire component
    const handleMouseLeave = () => {
      cleanup();
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      cleanup();
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

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
        
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <span>🔍</span>
          <span>Filters & Layout</span>
          {(filters.selectedOutcomes.length > 0 || filters.selectedDomain || filters.rootNodeId) && (
            <span className="bg-blue-500 text-xs px-2 py-0.5 rounded-full">
              {[filters.selectedOutcomes.length, filters.selectedDomain ? 1 : 0, filters.rootNodeId ? 1 : 0].reduce((a, b) => a + b, 0)}
            </span>
          )}
        </button>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="mb-4 bg-white border rounded-lg p-4 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-gray-900">Graph Filters & Layout</h4>
            <button
              onClick={() => setShowFilters(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Layout Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Layout</label>
              <select
                value={layoutMode}
                onChange={(e) => setLayoutMode(e.target.value as 'hierarchical' | 'centered')}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="hierarchical">Hierarchical</option>
                <option value="centered">Centered</option>
              </select>
            </div>
            
            {/* Domain Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Domain</label>
              <select
                value={filters.selectedDomain}
                onChange={(e) => setFilters({...filters, selectedDomain: e.target.value})}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Domains</option>
                {availableDomains.map(domain => (
                  <option key={domain} value={domain}>{domain}</option>
                ))}
              </select>
            </div>
            
            {/* Root Node Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Focus on Content</label>
              <select
                value={filters.rootNodeId || ''}
                onChange={(e) => setFilters({...filters, rootNodeId: e.target.value || null})}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Content</option>
                {nodes.map(node => (
                  <option key={node.id} value={node.id}>{node.name}</option>
                ))}
              </select>
            </div>
            
            {/* Status Filters */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <div className="space-y-2">
                <label className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={filters.showCompleted}
                    onChange={(e) => setFilters({...filters, showCompleted: e.target.checked})}
                    className="mr-2 rounded"
                  />
                  Completed
                </label>
                <label className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={filters.showInProgress}
                    onChange={(e) => setFilters({...filters, showInProgress: e.target.checked})}
                    className="mr-2 rounded"
                  />
                  In Progress
                </label>
                <label className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={filters.showNotStarted}
                    onChange={(e) => setFilters({...filters, showNotStarted: e.target.checked})}
                    className="mr-2 rounded"
                  />
                  Not Started
                </label>
              </div>
            </div>
            
            {/* Learning Outcomes */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Learning Outcomes</label>
              <div className="max-h-32 overflow-y-auto border border-gray-200 rounded-md p-2 bg-gray-50">
                {availableOutcomes.length > 0 ? (
                  <div className="space-y-1">
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
                          className="mr-2 rounded"
                        />
                        {outcome}
                      </label>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No outcomes available</p>
                )}
              </div>
            </div>
          </div>
          
          {/* Clear Filters */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={() => setFilters({
                showCompleted: true,
                showInProgress: true,
                showNotStarted: true,
                selectedOutcomes: [],
                selectedDomain: '',
                selectedDifficulty: '',
                rootNodeId: null
              })}
              className="text-sm text-gray-600 hover:text-gray-800 underline"
            >
              Clear all filters
            </button>
          </div>
        </div>
      )}
      
      <svg
        ref={svgRef}
        width="800"
        height="600"
        className="border rounded-lg bg-gray-50"
        onMouseLeave={() => {
          setHoveredNode(null);
          hideTooltip();
        }}
      />

      <div className="mt-4 text-xs text-gray-600 space-y-1">
        <p><strong>Layout:</strong> {layoutMode === 'hierarchical' ? 'Hierarchical view with root at top' : 'Centered view with selected root in middle'}</p>
        <p><strong>Interaction:</strong> Click nodes to set as root • Hover for details • Scroll to zoom • Drag to pan</p>
        <p><strong>Root Node:</strong> {filters.rootNodeId ? nodes.find(n => n.id === filters.rootNodeId)?.name || 'Selected' : 'None selected'} (red border)</p>
      </div>
    </div>
  );
}