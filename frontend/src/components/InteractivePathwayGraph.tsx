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
    minImpact: 0.1,
    showHighImpact: false
  });

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
      const response = await api.get(`/pathway/${pathwayId}/chain-analysis`);
      const data = response.data;
      
      setNodes(data.pathway_data.nodes);
      setChainImpacts(data.chain_analysis.node_importance || {});
    } catch (error) {
      console.error('Failed to load pathway data:', error);
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

    // Create all-to-all connections with chain rule weights
    const links = [];
    filteredNodes.forEach(source => {
      filteredNodes.forEach(target => {
        if (source.id !== target.id) {
          const sourceImportance = chainImpacts[source.id] || 0.1;
          const targetImportance = chainImpacts[target.id] || 0.1;
          const weight = sourceImportance * targetImportance;
          
          if (weight > 0.01) {
            links.push({
              source: source.id,
              target: target.id,
              weight: weight
            });
          }
        }
      });
    });

    // Force simulation
    const simulation = d3.forceSimulation(filteredNodes as any)
      .force('link', d3.forceLink(links).id((d: any) => d.id).strength(0.1))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius((d: any) => getNodeRadius(d) + 10));

    // Links (no arrowheads)
    const linkElements = svg.append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#94A3B8')
      .attr('stroke-width', (d: any) => Math.max(0.5, d.weight * 6))
      .attr('opacity', (d: any) => {
        if (!hoveredNode) return 0.1;
        return (d.source.id === hoveredNode || d.target.id === hoveredNode) ? 0.8 : 0.05;
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

  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Learning Impact Analysis</h3>
        
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
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.showHighImpact}
              onChange={(e) => setFilters({...filters, showHighImpact: e.target.checked})}
              className="mr-1"
            />
            High Impact Only
          </label>
          <div className="flex items-center">
            <span className="mr-2">Min Impact:</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={filters.minImpact}
              onChange={(e) => setFilters({...filters, minImpact: parseFloat(e.target.value)})}
              className="w-20"
            />
            <span className="ml-1 text-xs">{Math.round(filters.minImpact * 100)}%</span>
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
        <p><strong>Chain Rule Analysis:</strong> Circle size shows learning impact weight calculated using chain rule mathematics.</p>
        <p><strong>Interaction:</strong> Hover nodes to see connections and detailed metadata. All nodes connect to all others.</p>
        <p><strong>Translucency:</strong> Nodes are 50% transparent until hovered, then show full impact relationships.</p>
      </div>
    </div>
  );
}