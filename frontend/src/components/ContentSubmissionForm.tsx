'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';
import { ContentSubmissionRequest, ContentSubmissionResponse } from '@/types/api';

interface Props {
  onSubmissionStart: () => void;
  onSubmissionComplete: (result: ContentSubmissionResponse) => void;
  disabled?: boolean;
}

export default function ContentSubmissionForm({ onSubmissionStart, onSubmissionComplete, disabled }: Props) {
  const [formData, setFormData] = useState<ContentSubmissionRequest>({
    content: '',
    model_provider: 'openai',
    model_name: 'gpt-4',
    suggested_tier: 'T2',
    suggested_personas: ['developer'],
    suggested_content_type: 'lesson',
  });
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    onSubmissionStart();

    try {
      const result = await apiClient.submitContent(formData);
      onSubmissionComplete(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      onSubmissionComplete({
        workflow_id: 'error',
        status: 'error',
        extracted_metadata: {},
        similar_content: [],
        human_review_required: false,
        error_message: err instanceof Error ? err.message : 'An error occurred',
      });
    }
  };

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Submit Learning Content</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
            Learning Content *
          </label>
          <textarea
            id="content"
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Paste your learning content here..."
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            required
            disabled={disabled}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="tier" className="block text-sm font-medium text-gray-700 mb-2">
              Suggested Tier
            </label>
            <select
              id="tier"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              value={formData.suggested_tier}
              onChange={(e) => setFormData({ ...formData, suggested_tier: e.target.value })}
              disabled={disabled}
            >
              <option value="T1">T1 - Foundational</option>
              <option value="T2">T2 - Intermediate</option>
              <option value="T3">T3 - Advanced</option>
              <option value="T4">T4 - Expert</option>
            </select>
          </div>

          <div>
            <label htmlFor="content_type" className="block text-sm font-medium text-gray-700 mb-2">
              Content Type
            </label>
            <select
              id="content_type"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              value={formData.suggested_content_type}
              onChange={(e) => setFormData({ ...formData, suggested_content_type: e.target.value })}
              disabled={disabled}
            >
              <option value="lesson">Lesson</option>
              <option value="module">Module</option>
              <option value="exercise">Exercise</option>
              <option value="assessment">Assessment</option>
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="personas" className="block text-sm font-medium text-gray-700 mb-2">
            Target Personas
          </label>
          <select
            id="personas"
            multiple
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            value={formData.suggested_personas}
            onChange={(e) => setFormData({ 
              ...formData, 
              suggested_personas: Array.from(e.target.selectedOptions, option => option.value)
            })}
            disabled={disabled}
          >
            <option value="developer">Developer</option>
            <option value="architect">Architect</option>
            <option value="operations">Operations</option>
            <option value="security">Security</option>
            <option value="data_engineer">Data Engineer</option>
            <option value="ml_engineer">ML Engineer</option>
          </select>
          <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={disabled || !formData.content.trim()}
          className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {disabled ? 'Processing...' : 'Submit Content'}
        </button>
      </form>
    </div>
  );
}