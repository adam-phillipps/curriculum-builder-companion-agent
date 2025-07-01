'use client';

import { useState, useEffect } from 'react';
import ContentTile from './ContentTile';
import ContentPreviewModal from './ContentPreviewModal';
import ContentFilters from './ContentFilters';
import ContentViewer from './ContentViewer';
import { ApiClient } from '../../lib/api';

interface Content {
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
  similarity_score?: number;
}

export default function ContentManagement() {
  const [contents, setContents] = useState<Content[]>([]);
  const [filteredContents, setFilteredContents] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modal states
  const [selectedContent, setSelectedContent] = useState<Content | null>(null);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [viewingContentIds, setViewingContentIds] = useState<number[]>([]);
  
  // Filter states
  const [filters, setFilters] = useState({
    tier: '',
    personas: [] as string[],
    content_type: '',
    sandbox_type: ''
  });
  const [showFilters, setShowFilters] = useState(false);

  // Lazy load content - only fetch when tab is active
  useEffect(() => {
    let isMounted = true;
    
    const fetchContent = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const data = await ApiClient.searchContent({ max_results: 12 }); // Load fewer initially
        
        if (isMounted) {
          setContents(data.results || []);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load content');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    // Delay fetch to improve perceived performance
    const timer = setTimeout(fetchContent, 100);
    
    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, []);

  // Apply filters whenever filters or contents change
  useEffect(() => {
    let filtered = contents;

    if (filters.tier) {
      filtered = filtered.filter(content => content.tier === filters.tier);
    }

    if (filters.content_type) {
      filtered = filtered.filter(content => content.content_type === filters.content_type);
    }

    if (filters.sandbox_type) {
      filtered = filtered.filter(content => content.sandbox_type === filters.sandbox_type);
    }

    if (filters.personas.length > 0) {
      filtered = filtered.filter(content => 
        content.personas?.some(persona => filters.personas.includes(persona))
      );
    }

    setFilteredContents(filtered);
  }, [contents, filters]);

  const handleTileClick = (content: Content) => {
    setSelectedContent(content);
    setShowPreviewModal(true);
  };

  const handleClosePreviewModal = () => {
    setShowPreviewModal(false);
    setSelectedContent(null);
  };

  const handleViewContent = () => {
    if (selectedContent) {
      setViewingContentIds(prev => [...prev, selectedContent.content_id]);
      setShowPreviewModal(false);
      setSelectedContent(null);
    }
  };

  const handleCloseContentViewer = (contentId: number) => {
    setViewingContentIds(prev => prev.filter(id => id !== contentId));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading content...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 text-6xl mb-4">⚠️</div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Content</h2>
        <p className="text-gray-600 mb-4">{error}</p>
<div className="space-x-3">
          <button
            onClick={() => {
              setError(null);
              setLoading(true);
              // Trigger re-fetch by updating a dummy state
              setTimeout(() => window.location.reload(), 100);
            }}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Retry
          </button>
          <button
            onClick={() => setError(null)}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
          >
            Dismiss
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Content Management</h1>
        <p className="text-gray-600 mt-1">
          Browse and manage learning content. Found {filteredContents.length} items.
        </p>
      </div>

      {/* Filters */}
      <ContentFilters
        filters={filters}
        onFiltersChange={setFilters}
        isOpen={showFilters}
        onToggle={() => setShowFilters(!showFilters)}
      />

      {/* Content Grid */}
      {filteredContents.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📚</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Content Found</h3>
          <p className="text-gray-600">
            {contents.length === 0 
              ? "No content available yet." 
              : "Try adjusting your filters to see more content."
            }
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredContents.map((content) => (
            <ContentTile
              key={content.content_id}
              content={content}
              onClick={() => handleTileClick(content)}
            />
          ))}
        </div>
      )}

      {/* Preview Modal */}
      {selectedContent && (
        <ContentPreviewModal
          content={selectedContent}
          isOpen={showPreviewModal}
          onClose={handleClosePreviewModal}
          onViewContent={handleViewContent}
        />
      )}

      {/* Content Viewers */}
      {viewingContentIds.map((contentId) => (
        <ContentViewer
          key={contentId}
          contentId={contentId}
          onClose={() => handleCloseContentViewer(contentId)}
        />
      ))}
    </div>
  );
}