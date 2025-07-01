'use client';

import { useState, useEffect } from 'react';
import { Search, Filter, Clock, User, Tag, Zap } from 'lucide-react';

interface SearchResult {
  content_id: number;
  title: string;
  description: string;
  tier: string;
  content_type: string;
  similarity_score: number;
  personas?: string[];
  aws_services?: string[];
  estimated_duration: number;
  estimated_cost: number;
  sandbox_type?: string;
  author?: string;
  co_authors?: string[];
  sources?: string;
  artifacts?: string;
  ai_assisted?: string;
  tags?: string[];
  learning_objectives?: string[];
  created_at?: string;
  updated_at?: string;
  status?: string;
  is_approved?: boolean;
}

interface SearchResponse {
  results: SearchResult[];
  total_found: number;
  search_time_ms: number;
}

interface Props {
  onContentSelect?: (content: SearchResult) => void;
}

export default function ContentSearch({ onContentSelect }: Props) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchTime, setSearchTime] = useState<number | null>(null);
  const [filters, setFilters] = useState({
    tier: '',
    content_type: '',
    sandbox_type: '',
    author: '',
    personas: [] as string[],
    tags: [] as string[],
    duration_min: '',
    duration_max: '',
    cost_min: '',
    cost_max: '',
    created_after: '',
    created_before: '',
    updated_after: '',
    updated_before: '',
    search_approved_only: false,
    similarity_threshold: 0.3
  });
  const [showFilters, setShowFilters] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsSearching(true);
    try {
      const response = await fetch('/api/v1/vector/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query_text: query,
          metadata_filters: {
            ...(filters.tier && { tier: filters.tier }),
            ...(filters.content_type && { content_type: filters.content_type }),
            ...(filters.sandbox_type && { sandbox_type: filters.sandbox_type }),
            ...(filters.author && { author: filters.author }),
            ...(filters.personas.length > 0 && { personas: filters.personas }),
            ...(filters.tags.length > 0 && { tags: filters.tags }),
            ...(filters.duration_min && { duration_min: parseInt(filters.duration_min) }),
            ...(filters.duration_max && { duration_max: parseInt(filters.duration_max) }),
            ...(filters.cost_min && { cost_min: parseFloat(filters.cost_min) }),
            ...(filters.cost_max && { cost_max: parseFloat(filters.cost_max) }),
            ...(filters.created_after && { created_after: filters.created_after }),
            ...(filters.created_before && { created_before: filters.created_before }),
            ...(filters.updated_after && { updated_after: filters.updated_after }),
            ...(filters.updated_before && { updated_before: filters.updated_before })
          },
          similarity_threshold: filters.similarity_threshold,
          max_results: 20,
          search_approved_only: filters.search_approved_only
        })
      });

      if (!response.ok) throw new Error('Search failed');
      
      const data: SearchResponse = await response.json();
      setResults(data.results);
      setSearchTime(data.search_time_ms);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getTierColor = (tier: string) => {
    const colors = {
      T1: 'bg-green-100 text-green-800',
      T2: 'bg-blue-100 text-blue-800', 
      T3: 'bg-orange-100 text-orange-800',
      T4: 'bg-red-100 text-red-800'
    };
    return colors[tier as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 0.8) return 'text-red-600 font-semibold';
    if (score >= 0.6) return 'text-orange-600 font-medium';
    return 'text-green-600';
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Search Content</h2>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="btn-secondary text-sm"
        >
          <Filter className="w-4 h-4 mr-1" />
          Filters
        </button>
      </div>

      {/* Search Input */}
      <div className="flex space-x-3 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search for similar content..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={!query.trim() || isSearching}
          className="btn-primary disabled:opacity-50"
        >
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4 space-y-4">
          {/* Basic Filters */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Difficulty Tier</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={filters.tier}
                onChange={(e) => setFilters({...filters, tier: e.target.value})}
              >
                <option value="">All Tiers</option>
                <option value="T1">T1 - Foundational</option>
                <option value="T2">T2 - Intermediate</option>
                <option value="T3">T3 - Advanced</option>
                <option value="T4">T4 - Expert</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={filters.content_type}
                onChange={(e) => setFilters({...filters, content_type: e.target.value})}
              >
                <option value="">All Types</option>
                <option value="lesson">Lesson</option>
                <option value="module">Module</option>
                <option value="exercise">Exercise</option>
                <option value="assessment">Assessment</option>
                <option value="session">Session</option>
                <option value="experiment">Experiment</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Sandbox Requirements</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={filters.sandbox_type}
                onChange={(e) => setFilters({...filters, sandbox_type: e.target.value})}
              >
                <option value="">Any Sandbox</option>
                <option value="individual">Individual</option>
                <option value="shared">Shared</option>
                <option value="isolated">Isolated</option>
                <option value="managed">Managed</option>
              </select>
            </div>
          </div>

          {/* Author and Role Filters */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Author</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Search by author name"
                value={filters.author}
                onChange={(e) => setFilters({...filters, author: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Target Roles</label>
              <select
                multiple
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={filters.personas}
                onChange={(e) => setFilters({...filters, personas: Array.from(e.target.selectedOptions, option => option.value)})}
              >
                <option value="developer">Developer</option>
                <option value="architect">Solution Architect</option>
                <option value="operations">Operations Engineer</option>
                <option value="security">Security Engineer</option>
                <option value="data_engineer">Data Engineer</option>
                <option value="ml_engineer">ML Engineer</option>
                <option value="all_roles">All Roles</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
            </div>
          </div>

          {/* Tags Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., lambda, serverless, python (comma-separated)"
              value={filters.tags.join(', ')}
              onChange={(e) => setFilters({...filters, tags: e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag)})}
            />
          </div>

          {/* Duration and Cost Ranges */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Duration (minutes)</label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  placeholder="Min"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={filters.duration_min}
                  onChange={(e) => setFilters({...filters, duration_min: e.target.value})}
                />
                <span className="self-center text-gray-500">to</span>
                <input
                  type="number"
                  placeholder="Max"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={filters.duration_max}
                  onChange={(e) => setFilters({...filters, duration_max: e.target.value})}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Cost Estimate ($)</label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  step="0.01"
                  placeholder="Min"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={filters.cost_min}
                  onChange={(e) => setFilters({...filters, cost_min: e.target.value})}
                />
                <span className="self-center text-gray-500">to</span>
                <input
                  type="number"
                  step="0.01"
                  placeholder="Max"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={filters.cost_max}
                  onChange={(e) => setFilters({...filters, cost_max: e.target.value})}
                />
              </div>
            </div>
          </div>

          {/* Date Filters */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Created Date</label>
              <div className="flex space-x-2">
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={filters.created_after}
                  onChange={(e) => setFilters({...filters, created_after: e.target.value})}
                />
                <span className="self-center text-gray-500">to</span>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={filters.created_before}
                  onChange={(e) => setFilters({...filters, created_before: e.target.value})}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Last Updated</label>
              <div className="flex space-x-2">
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={filters.updated_after}
                  onChange={(e) => setFilters({...filters, updated_after: e.target.value})}
                />
                <span className="self-center text-gray-500">to</span>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  value={filters.updated_before}
                  onChange={(e) => setFilters({...filters, updated_before: e.target.value})}
                />
              </div>
            </div>
          </div>

          {/* Options */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="approved-only"
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  checked={filters.search_approved_only}
                  onChange={(e) => setFilters({...filters, search_approved_only: e.target.checked})}
                />
                <label htmlFor="approved-only" className="ml-2 text-sm text-gray-700">
                  Approved content only
                </label>
              </div>

              <div className="flex items-center space-x-2">
                <label className="text-sm text-gray-700">Similarity:</label>
                <input
                  type="range"
                  min="0.1"
                  max="1"
                  step="0.1"
                  value={filters.similarity_threshold}
                  onChange={(e) => setFilters({...filters, similarity_threshold: parseFloat(e.target.value)})}
                  className="w-20"
                />
                <span className="text-sm text-gray-600">{Math.round(filters.similarity_threshold * 100)}%</span>
              </div>
            </div>

            <button
              onClick={() => setFilters({
                tier: '', content_type: '', sandbox_type: '', author: '', personas: [], tags: [],
                duration_min: '', duration_max: '', cost_min: '', cost_max: '',
                created_after: '', created_before: '', updated_after: '', updated_before: '',
                search_approved_only: false, similarity_threshold: 0.3
              })}
              className="text-sm text-gray-600 hover:text-gray-800 underline"
            >
              Clear All Filters
            </button>
          </div>
        </div>
      )}

      {/* Search Results */}
      {searchTime !== null && (
        <div className="text-sm text-gray-500 mb-4">
          Found {results.length} results in {searchTime.toFixed(0)}ms
        </div>
      )}

      <div className="space-y-4">
        {results.map((result) => (
          <div
            key={result.content_id}
            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
            onClick={() => onContentSelect?.(result)}
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-medium text-gray-900">{result.title}</h3>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTierColor(result.tier)}`}>
                  {result.tier}
                </span>
                <span className={`text-sm ${getSimilarityColor(result.similarity_score)}`}>
                  {Math.round(result.similarity_score * 100)}%
                </span>
              </div>
            </div>

            <p className="text-gray-600 text-sm mb-3 overflow-hidden" style={{display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical'}}>{result.description}</p>

            <div className="space-y-2">
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <div className="flex items-center">
                  <Tag className="w-3 h-3 mr-1" />
                  {result.content_type}
                </div>
                <div className="flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {result.estimated_duration}min
                </div>
                <div className="flex items-center">
                  <User className="w-3 h-3 mr-1" />
                  {result.personas?.join(', ') || 'N/A'}
                </div>
                {result.estimated_cost > 0 && (
                  <div className="flex items-center">
                    <span className="w-3 h-3 mr-1">$</span>
                    {result.estimated_cost}
                  </div>
                )}
                {result.aws_services?.length > 0 && (
                  <div className="flex items-center">
                    <Zap className="w-3 h-3 mr-1" />
                    {result.aws_services.join(', ')}
                  </div>
                )}
              </div>
              
              {/* Additional metadata row */}
              <div className="flex items-center space-x-4 text-xs text-gray-400">
                {result.author && (
                  <div>Author: {result.author}</div>
                )}
                {result.sandbox_type && (
                  <div>Sandbox: {result.sandbox_type}</div>
                )}
                {result.tags?.length > 0 && (
                  <div>Tags: {result.tags.join(', ')}</div>
                )}
                {result.created_at && (
                  <div>Created: {new Date(result.created_at).toLocaleDateString()}</div>
                )}
              </div>
            </div>
          </div>
        ))}

        {results.length === 0 && query && !isSearching && (
          <div className="text-center py-8 text-gray-500">
            <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No content found matching your search</p>
          </div>
        )}

        {!query && (
          <div className="text-center py-8 text-gray-500">
            <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>Enter a search query to find similar content</p>
          </div>
        )}
      </div>
    </div>
  );
}