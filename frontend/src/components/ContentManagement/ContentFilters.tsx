'use client';

import { Filter } from 'lucide-react';

interface ContentFiltersProps {
  filters: {
    tier: string;
    personas: string[];
    content_type: string;
    sandbox_type: string;
  };
  onFiltersChange: (filters: any) => void;
  isOpen: boolean;
  onToggle: () => void;
}

export default function ContentFilters({ 
  filters, 
  onFiltersChange, 
  isOpen, 
  onToggle 
}: ContentFiltersProps) {
  const updateFilter = (key: string, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
      >
        <div className="flex items-center">
          <Filter className="w-5 h-5 mr-2 text-gray-500" />
          <span className="font-medium text-gray-900">Filters</span>
        </div>
        <span className="text-gray-400">
          {isOpen ? '−' : '+'}
        </span>
      </button>

      {isOpen && (
        <div className="border-t border-gray-200 p-4 space-y-4">
          {/* Difficulty Tier */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Difficulty Tier
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              value={filters.tier}
              onChange={(e) => updateFilter('tier', e.target.value)}
            >
              <option value="">All Tiers</option>
              <option value="T1">T1 - Foundational</option>
              <option value="T2">T2 - Intermediate</option>
              <option value="T3">T3 - Advanced</option>
              <option value="T4">T4 - Expert</option>
            </select>
          </div>

          {/* Target Learner Roles */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Learner Roles
            </label>
            <select
              multiple
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              value={filters.personas}
              onChange={(e) => updateFilter('personas', Array.from(e.target.selectedOptions, option => option.value))}
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

          {/* Content Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content Type
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              value={filters.content_type}
              onChange={(e) => updateFilter('content_type', e.target.value)}
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

          {/* Sandbox Environment */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sandbox Environment
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              value={filters.sandbox_type}
              onChange={(e) => updateFilter('sandbox_type', e.target.value)}
            >
              <option value="">Any Environment</option>
              <option value="individual">Individual</option>
              <option value="shared">Shared</option>
              <option value="isolated">Isolated</option>
              <option value="managed">Managed</option>
            </select>
          </div>

          {/* Clear Filters */}
          <button
            onClick={() => onFiltersChange({
              tier: '',
              personas: [],
              content_type: '',
              sandbox_type: ''
            })}
            className="w-full text-sm text-gray-600 hover:text-gray-800 underline"
          >
            Clear All Filters
          </button>
        </div>
      )}
    </div>
  );
}