'use client';

import { ContentSubmissionResponse } from '@/types/api';
import { CheckCircle, Clock, AlertCircle, RefreshCw } from 'lucide-react';

interface Props {
  result: ContentSubmissionResponse | null;
  isProcessing: boolean;
  onReset: () => void;
}

export default function WorkflowProgress({ result, isProcessing, onReset }: Props) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'published':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'text-green-700 bg-green-50 border-green-200';
      case 'error':
        return 'text-red-700 bg-red-50 border-red-200';
      default:
        return 'text-yellow-700 bg-yellow-50 border-yellow-200';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Workflow Progress</h2>
        {result && (
          <button
            onClick={onReset}
            className="btn-secondary text-sm"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Reset
          </button>
        )}
      </div>

      {isProcessing && (
        <div className="flex items-center space-x-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          <span className="text-blue-700">Processing your content...</span>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          {/* Status */}
          <div className={`flex items-center space-x-3 p-4 border rounded-lg ${getStatusColor(result.status)}`}>
            {getStatusIcon(result.status)}
            <div>
              <p className="font-medium">Status: {result.status}</p>
              <p className="text-sm">Workflow ID: {result.workflow_id}</p>
            </div>
          </div>

          {/* Error Message */}
          {result.error_message && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h3 className="font-medium text-red-800 mb-2">Error Details</h3>
              <p className="text-sm text-red-600">{result.error_message}</p>
            </div>
          )}

          {/* Extracted Metadata */}
          {Object.keys(result.extracted_metadata).length > 0 && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-800 mb-2">Extracted Metadata</h3>
              <div className="space-y-2 text-sm">
                {result.extracted_metadata.title && (
                  <div>
                    <span className="font-medium">Title:</span> {result.extracted_metadata.title}
                  </div>
                )}
                {result.extracted_metadata.tier && (
                  <div>
                    <span className="font-medium">Tier:</span> {result.extracted_metadata.tier}
                  </div>
                )}
                {result.extracted_metadata.content_type && (
                  <div>
                    <span className="font-medium">Type:</span> {result.extracted_metadata.content_type}
                  </div>
                )}
                {result.extracted_metadata.estimated_duration && (
                  <div>
                    <span className="font-medium">Duration:</span> {result.extracted_metadata.estimated_duration} minutes
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Similar Content */}
          {result.similar_content.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="font-medium text-yellow-800 mb-2">
                Similar Content Found ({result.similar_content.length})
              </h3>
              <div className="space-y-2">
                {result.similar_content.map((item, index) => (
                  <div key={index} className="text-sm bg-white p-3 rounded border">
                    <div className="font-medium">{item.title}</div>
                    <div className="text-gray-600">
                      {item.tier} • {item.content_type} • 
                      Similarity: {Math.round(item.similarity_score * 100)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Human Review Required */}
          {result.human_review_required && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <h3 className="font-medium text-orange-800 mb-2">Human Review Required</h3>
              <p className="text-sm text-orange-600">
                This content requires human review before publication due to high similarity scores or other factors.
              </p>
            </div>
          )}

          {/* Success Message */}
          {result.status === 'published' && result.content_id && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="font-medium text-green-800 mb-2">Content Published Successfully!</h3>
              <p className="text-sm text-green-600">
                Content ID: {result.content_id}
              </p>
            </div>
          )}
        </div>
      )}

      {!isProcessing && !result && (
        <div className="text-center py-8 text-gray-500">
          <Clock className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>Submit content to see workflow progress</p>
        </div>
      )}
    </div>
  );
}