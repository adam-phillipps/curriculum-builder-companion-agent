'use client';

import { useState, useEffect } from 'react';

interface PathwayNode {
  id: string;
  name: string;
  category: string;
  completion: number;
  weight: number;
  level: number;
}

interface PathwayLink {
  source: string;
  target: string;
  value: number;
  weight: number;
}

interface SankeyPathwayDiagramProps {
  userId: number;
  pathwayId?: number;
  zoomLevel: 'content' | 'pathway' | 'journey';
}

export default function SankeyPathwayDiagram({ userId, pathwayId, zoomLevel }: SankeyPathwayDiagramProps) {
  const [nodes, setNodes] = useState<PathwayNode[]>([]);
  const [links, setLinks] = useState<PathwayLink[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPathwayData();
  }, [userId, pathwayId, zoomLevel]);

  const loadPathwayData = async () => {
    setLoading(true);
    try {
      // Simulate API call - replace with real API
      const mockData = generateMockPathwayData(zoomLevel);
      setNodes(mockData.nodes);
      setLinks(mockData.links);
    } catch (error) {
      console.error('Failed to load pathway data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockPathwayData = (level: string) => {
    if (level === 'content') {
      return {
        nodes: [
          { id: 'calculus', name: 'Calculus Fundamentals', category: 'math', completion: 0.9, weight: 0.6, level: 0 },
          { id: 'linear_algebra', name: 'Linear Algebra', category: 'math', completion: 0.7, weight: 0.8, level: 1 },
          { id: 'algorithms', name: 'Algorithms & Data Structures', category: 'cs', completion: 0.4, weight: 0.7, level: 1 },
          { id: 'python_ml', name: 'Python for ML', category: 'programming', completion: 0.8, weight: 0.9, level: 1 },
          { id: 'mlops', name: 'MLOps Fundamentals', category: 'engineering', completion: 0.6, weight: 0.7, level: 2 },
          { id: 'neural_nets', name: 'Build Neural Net from Scratch', category: 'ml', completion: 0.2, weight: 1.0, level: 3 }
        ],
        links: [
          { source: 'calculus', target: 'linear_algebra', value: 0.6, weight: 0.8 },
          { source: 'linear_algebra', target: 'neural_nets', value: 0.8, weight: 0.9 },
          { source: 'algorithms', target: 'python_ml', value: 0.4, weight: 0.6 },
          { source: 'python_ml', target: 'mlops', value: 0.8, weight: 0.7 },
          { source: 'mlops', target: 'neural_nets', value: 0.6, weight: 0.8 },
          { source: 'python_ml', target: 'neural_nets', value: 0.8, weight: 0.5 }
        ]
      };
    }
    return { nodes: [], links: [] };
  };

  const getNodeColor = (category: string, completion: number) => {
    const baseColors = {
      math: '#3B82F6',
      cs: '#10B981', 
      programming: '#F59E0B',
      engineering: '#8B5CF6',
      ml: '#EF4444'
    };
    const opacity = 0.3 + (completion * 0.7);
    return `${baseColors[category as keyof typeof baseColors]}${Math.round(opacity * 255).toString(16)}`;
  };

  const renderSimpleSankey = () => {
    const levels = [0, 1, 2, 3];
    const levelWidth = 200;
    const nodeHeight = 60;
    const nodeSpacing = 80;

    return (
      <svg width="800" height="400" className="border rounded-lg bg-white">
        {/* Render links first (behind nodes) */}
        {links.map((link, index) => {
          const sourceNode = nodes.find(n => n.id === link.source);
          const targetNode = nodes.find(n => n.id === link.target);
          if (!sourceNode || !targetNode) return null;

          const x1 = sourceNode.level * levelWidth + 150;
          const y1 = levels.indexOf(sourceNode.level) * nodeSpacing + 100;
          const x2 = targetNode.level * levelWidth + 50;
          const y2 = levels.indexOf(targetNode.level) * nodeSpacing + 100;

          return (
            <path
              key={index}
              d={`M ${x1} ${y1} Q ${(x1 + x2) / 2} ${y1} ${x2} ${y2}`}
              stroke="#94A3B8"
              strokeWidth={link.weight * 8}
              fill="none"
              opacity={0.6}
            />
          );
        })}

        {/* Render nodes */}
        {nodes.map((node, index) => {
          const x = node.level * levelWidth + 50;
          const y = index * nodeSpacing + 50;

          return (
            <g key={node.id}>
              <rect
                x={x}
                y={y}
                width={120}
                height={nodeHeight}
                rx={8}
                fill={getNodeColor(node.category, node.completion)}
                stroke="#E5E7EB"
                strokeWidth={2}
              />
              <text
                x={x + 60}
                y={y + 25}
                textAnchor="middle"
                className="text-xs font-medium fill-gray-800"
              >
                {node.name.split(' ').slice(0, 2).join(' ')}
              </text>
              <text
                x={x + 60}
                y={y + 40}
                textAnchor="middle"
                className="text-xs fill-gray-600"
              >
                {Math.round(node.completion * 100)}% complete
              </text>
            </g>
          );
        })}
      </svg>
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
          <button className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded">
            Content View
          </button>
          <button className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded">
            Pathway View
          </button>
          <button className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded">
            Journey View
          </button>
        </div>
      </div>

      {renderSimpleSankey()}

      <div className="mt-4 grid grid-cols-5 gap-2 text-xs">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-400 rounded mr-2"></div>
          <span>Mathematics</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-400 rounded mr-2"></div>
          <span>Computer Science</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-yellow-400 rounded mr-2"></div>
          <span>Programming</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-purple-400 rounded mr-2"></div>
          <span>Engineering</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-red-400 rounded mr-2"></div>
          <span>Machine Learning</span>
        </div>
      </div>
    </div>
  );
}