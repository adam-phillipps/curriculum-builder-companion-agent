'use client';

import { X } from 'lucide-react';

interface ContentPreviewModalProps {
  content: {
    content_id: number;
    title: string;
    description: string;
    tier: string;
    content_type: string;
    estimated_duration: number;
    learning_objectives?: string[];
    personas?: string[];
    author?: string;
    sandbox_type?: string;
    aws_services?: string[];
  };
  isOpen: boolean;
  onClose: () => void;
  onViewContent: () => void;
}

export default function ContentPreviewModal({ 
  content, 
  isOpen, 
  onClose, 
  onViewContent 
}: ContentPreviewModalProps) {
  if (!isOpen) return null;

  const getTierColor = (tier: string) => {
    const colors = {
      T1: 'bg-green-100 text-green-800',
      T2: 'bg-blue-100 text-blue-800',
      T3: 'bg-orange-100 text-orange-800',
      T4: 'bg-red-100 text-red-800'
    };
    return colors[tier as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b">
          <div className="flex-1 pr-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {content.title}
            </h2>
            <div className="flex items-center space-x-3">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTierColor(content.tier)}`}>
                {content.tier}
              </span>
              <span className="text-sm text-gray-600 capitalize">
                {content.content_type}
              </span>
              <span className="text-sm text-gray-600">
                {content.estimated_duration} minutes
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Description */}
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Overview</h3>
            <p className="text-gray-700 leading-relaxed">
              {content.description}
            </p>
          </div>

          {/* Learning Objectives */}
          {content.learning_objectives && content.learning_objectives.length > 0 && (
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Learning Objectives</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                {content.learning_objectives.map((objective, index) => (
                  <li key={index}>{objective}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Target Audience */}
          {content.personas && content.personas.length > 0 && (
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Target Audience</h3>
              <div className="flex flex-wrap gap-2">
                {content.personas.map((persona, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm capitalize"
                  >
                    {persona.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Technical Details */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            {content.author && (
              <div>
                <span className="font-medium text-gray-900">Author:</span>
                <span className="ml-2 text-gray-700">{content.author}</span>
              </div>
            )}
            {content.sandbox_type && (
              <div>
                <span className="font-medium text-gray-900">Sandbox:</span>
                <span className="ml-2 text-gray-700 capitalize">{content.sandbox_type}</span>
              </div>
            )}
            <div>
              <span className="font-medium text-gray-900">Content ID:</span>
              <span className="ml-2 text-gray-700">{content.content_id}</span>
            </div>
          </div>

          {/* AWS Services */}
          {content.aws_services && content.aws_services.length > 0 && (
            <div>
              <h3 className="font-medium text-gray-900 mb-2">AWS Services</h3>
              <div className="flex flex-wrap gap-2">
                {content.aws_services.map((service, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm"
                  >
                    {service}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Go Back
          </button>
          <button
            onClick={onViewContent}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            View Content
          </button>
        </div>
      </div>
    </div>
  );
}