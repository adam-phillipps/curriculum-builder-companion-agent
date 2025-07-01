'use client';

interface ContentTileProps {
  content: {
    content_id: number;
    title: string;
    estimated_duration: number;
    tier: string;
    content_type: string;
    description?: string;
    personas?: string[];
    author?: string;
  };
  onClick: () => void;
}

export default function ContentTile({ content, onClick }: ContentTileProps) {
  const getTierColor = (tier: string) => {
    const colors = {
      T1: 'bg-green-100 text-green-800 border-green-200',
      T2: 'bg-blue-100 text-blue-800 border-blue-200',
      T3: 'bg-orange-100 text-orange-800 border-orange-200',
      T4: 'bg-red-100 text-red-800 border-red-200'
    };
    return colors[tier as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getTypeIcon = (type: string) => {
    const icons = {
      lesson: '📖',
      module: '📚',
      exercise: '💻',
      assessment: '✅',
      session: '🎯',
      experiment: '🧪'
    };
    return icons[type as keyof typeof icons] || '📄';
  };

  return (
    <div
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg hover:border-primary-300 cursor-pointer transition-all duration-200 h-48 flex flex-col justify-between"
    >
      <div>
        <div className="flex items-start justify-between mb-3">
          <span className="text-2xl">{getTypeIcon(content.content_type)}</span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getTierColor(content.tier)}`}>
            {content.tier}
          </span>
        </div>
        
        <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2 text-sm leading-tight">
          {content.title}
        </h3>
        
        {content.description && (
          <p className="text-xs text-gray-600 line-clamp-2 mb-3">
            {content.description}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span className="capitalize">{content.content_type}</span>
          <span>{content.estimated_duration} min</span>
        </div>
        
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-400">ID: {content.content_id}</span>
          {content.author && (
            <span className="text-gray-500 truncate max-w-20">{content.author}</span>
          )}
        </div>
      </div>
    </div>
  );
}