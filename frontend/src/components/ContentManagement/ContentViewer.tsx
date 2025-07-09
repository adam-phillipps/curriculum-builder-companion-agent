'use client';

import { X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { ApiClient } from '../../lib/api';

interface ContentViewerProps {
  contentId: number;
  onClose: () => void;
}

interface FullContent {
  id: number;
  title: string;
  description: string;
  content_type: string;
  tier: string;
  learning_objectives: string[];
  estimated_duration: number;
  personas: string[];
  author?: string;
  // This contains the actual learning content
  content_body?: string;
}

/**
 * Full-screen content viewer component for displaying learning content details.
 * 
 * Fetches and displays complete learning content including objectives,
 * descriptions, target audience, and technical requirements.
 * 
 * Parameters
 * ----------
 * contentId : number
 *     The unique identifier of the content to display
 * onClose : () => void
 *     Callback function to close the content viewer
 * 
 * Returns
 * -------
 * JSX.Element
 *     Full-screen modal with content details or loading/error states
 */
export default function ContentViewer({ contentId, onClose }: ContentViewerProps) {
  const [content, setContent] = useState<FullContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    /**
     * Fetch content details for the specified content ID.
     * 
     * Retrieves all content from the API and finds the specific item
     * by ID since individual content endpoints may not be available.
     * 
     * Parameters
     * ----------
     * contentId : number
     *     The ID of the content item to fetch
     * 
     * Side Effects
     * ------------
     * - Sets loading state during fetch
     * - Updates content state with fetched data
     * - Sets error state if fetch fails
     */
    const fetchContent = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Get specific content item by ID
        const response = await fetch(`http://localhost:8001/api/v1/content/${contentId}`);
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error(`Content with ID ${contentId} not found`);
          }
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        setContent(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load content';
        setError(errorMessage);
        console.error('Content fetch failed:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, [contentId]);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-white z-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading content...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-white z-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Content</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!content) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-white z-50 overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{content.title}</h1>
          <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
            <span className="capitalize">{content.content_type}</span>
            <span>{content.tier}</span>
            <span>{content.estimated_duration} minutes</span>
            {content.author && <span>by {content.author}</span>}
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors p-2"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Overview Section */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Overview</h2>
          <p className="text-gray-700 leading-relaxed">{content.description}</p>
        </div>

        {/* Learning Objectives */}
        {content.learning_objectives && content.learning_objectives.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Learning Objectives</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              {content.learning_objectives.map((objective, index) => (
                <li key={index}>{objective}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Main Content */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Content</h2>
          <div className="prose max-w-none">
            {content.content_body ? (
              <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {content.content_body}
              </div>
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
                <div className="text-4xl mb-4">📚</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Content Coming Soon</h3>
                <p className="text-gray-600">
                  The full content for this {content.content_type} is being prepared and will be available soon.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Target Audience */}
        {content.personas && content.personas.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Target Audience</h2>
            <div className="flex flex-wrap gap-2">
              {content.personas.map((persona, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm capitalize"
                >
                  {persona.replace('_', ' ')}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}