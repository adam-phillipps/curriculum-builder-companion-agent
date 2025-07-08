'use client';

import { useState, useEffect } from 'react';

interface PathwayNode {
  id: string;
  content_id: number;
  weight: number;
  prerequisites: number[];
  status: string;
  completion: number;
  success_score: number | null;
}

interface DirectedGraphPathwayProps {
  userId: number;
  pathwayId?: number;
  zoomLevel: 'content' | 'pathway' | 'journey';
  onZoomChange: (level: 'content' | 'pathway' | 'journey') => void;
}

export default function DirectedGraphPathway({ userId, pathwayId, zoomLevel, onZoomChange }: DirectedGraphPathwayProps) {
  const [nodes, setNodes] = useState<PathwayNode[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPathwayData();
  }, [userId, pathwayId, zoomLevel]);

  const loadPathwayData = async () => {
    setLoading(true);
    try {
      // Mock data matching our JSON structure
      const mockNodes: PathwayNode[] = [
        { id: 'content_1', content_id: 1, weight: 0.6, prerequisites: [], status: 'completed', completion: 90, success_score: 0.9 },
        { id: 'content_2', content_id: 2, weight: 0.8, prerequisites: [1], status: 'completed', completion: 75, success_score: 0.75 },
        { id: 'content_3', content_id: 3, weight: 0.7, prerequisites: [], status: 'in_progress', completion: 40, success_score: 0.4 },
        { id: 'content_4', content_id: 4, weight: 0.9, prerequisites: [3], status: 'completed', completion: 85, success_score: 0.85 },
        { id: 'content_5', content_id: 5, weight: 0.7, prerequisites: [4], status: 'in_progress', completion: 60, success_score: 0.6 },
        { id: 'content_6', content_id: 6, weight: 1.0, prerequisites: [2, 5], status: 'not_started', completion: 0, success_score: null }
      ];
      setNodes(mockNodes);
    } catch (error) {
      console.error('Failed to load pathway data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getNodeRadius = (weight: number) => Math.max(20, weight * 40);
  
  const getNodeColor = (status: string, completion: number) => {
    if (status === 'completed') return '#10B981';
    if (status === 'in_progress') return '#F59E0B';
    return '#6B7280';
  };

  const getNodePosition = (nodeId: string, index: number) => {
    const positions = {
      'content_1': { x: 100, y: 100 },
      'content_2': { x: 300, y: 80 },
      'content_3': { x: 100, y: 200 },
      'content_4': { x: 300, y: 180 },
      'content_5': { x: 500, y: 160 },
      'content_6': { x: 700, y: 130 }
    };
    return positions[nodeId as keyof typeof positions] || { x: 100 + index * 100, y: 100 };
  };

  const renderArrow = (from: PathwayNode, to: PathwayNode) => {
    const fromPos = getNodePosition(from.id, 0);
    const toPos = getNodePosition(to.id, 0);
    const fromRadius = getNodeRadius(from.weight);
    const toRadius = getNodeRadius(to.weight);
    
    // Calculate arrow positions accounting for circle radius
    const dx = toPos.x - fromPos.x;
    const dy = toPos.y - fromPos.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const unitX = dx / distance;
    const unitY = dy / distance;
    
    const startX = fromPos.x + unitX * fromRadius;
    const startY = fromPos.y + unitY * fromRadius;
    const endX = toPos.x - unitX * toRadius;
    const endY = toPos.y - unitY * toRadius;
    
    return (
      <g key={`${from.id}-${to.id}`}>
        <line
          x1={startX}
          y1={startY}
          x2={endX}
          y2={endY}
          stroke="#94A3B8"
          strokeWidth={2}
          markerEnd="url(#arrowhead)"
        />
      </g>
    );
  };

  if (loading) {
    return <div className="p-6">Loading pathway visualization...</div>;
  }

  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Learning Pathway: Neural Networks</h3>
        <div className="flex space-x-2">
          {(['content', 'pathway', 'journey'] as const).map((level) => (
            <button
              key={level}
              onClick={() => onZoomChange(level)}
              className={`px-3 py-1 text-xs rounded ${
                zoomLevel === level 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)} View
            </button>
          ))}
        </div>
      </div>

      <svg width="800" height="300" className="border rounded-lg bg-gray-50">
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="7"
            refX="9"
            refY="3.5"
            orient="auto"
          >
            <polygon
              points="0 0, 10 3.5, 0 7"
              fill="#94A3B8"
            />
          </marker>
        </defs>

        {/* Render arrows first (behind nodes) */}
        {nodes.map(node => 
          node.prerequisites.map(prereqId => {
            const prereqNode = nodes.find(n => n.content_id === prereqId);
            return prereqNode ? renderArrow(prereqNode, node) : null;
          })
        ).flat()}

        {/* Render nodes */}
        {nodes.map((node, index) => {
          const pos = getNodePosition(node.id, index);
          const radius = getNodeRadius(node.weight);
          const color = getNodeColor(node.status, node.completion);

          return (
            <g key={node.id}>
              <circle
                cx={pos.x}
                cy={pos.y}
                r={radius}
                fill={color}
                stroke="#E5E7EB"
                strokeWidth={2}
                opacity={0.8}
              />
              <text
                x={pos.x}
                y={pos.y - 5}
                textAnchor="middle"
                className="text-xs font-medium fill-white"
              >
                Content {node.content_id}
              </text>
              <text
                x={pos.x}
                y={pos.y + 8}
                textAnchor="middle"
                className="text-xs fill-white"
              >
                {node.completion}%
              </text>
            </g>
          );
        })}
      </svg>

      <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
          <span>Completed</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
          <span>In Progress</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-gray-500 rounded-full mr-2"></div>
          <span>Not Started</span>
        </div>
      </div>
    </div>
  );
}