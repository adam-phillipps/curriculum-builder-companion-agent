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
    title: '',
    model_provider: 'openai',
    model_name: 'gpt-4',
    suggested_tier: 'T2',
    suggested_personas: ['developer'],
    suggested_content_type: 'lesson',
    suggested_tags: [],
    suggested_duration: 60,
    suggested_sandbox_type: 'individual',
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
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
            Content Title
          </label>
          <input
            id="title"
            type="text"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="e.g., 'Getting Started with AWS Lambda'"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            disabled={disabled}
          />
          <p className="text-xs text-gray-500 mt-1">Optional - AI will generate a title if not provided</p>
        </div>

        <div>
          <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
            Learning Content *
          </label>
          <div className="mb-2 text-sm text-gray-600 bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p><strong>📚 Submit Your Complete Learning Content</strong></p>
            <p>Paste the full learning material that students will use to learn. This could be:</p>
            <ul className="list-disc list-inside mt-1 text-xs">
              <li>Tutorial text with step-by-step instructions</li>
              <li>Course module content with explanations and examples</li>
              <li>Lab exercise instructions and code samples</li>
              <li>Complete lesson content ready for learners</li>
            </ul>
          </div>
          <textarea
            id="content"
            rows={8}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="Example: 'AWS Lambda Tutorial - Getting Started\n\nIn this tutorial, you will learn how to create your first AWS Lambda function using Python. We will cover:\n\n1. Setting up your development environment\n2. Creating a basic Lambda function\n3. Testing your function locally\n4. Deploying to AWS...'"
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            required
            disabled={disabled}
          />
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label htmlFor="tier" className="block text-sm font-medium text-gray-700 mb-2">
              Difficulty Tier
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
              <option value="session">Session</option>
              <option value="experiment">Experiment</option>
            </select>
          </div>

          <div>
            <label htmlFor="duration" className="block text-sm font-medium text-gray-700 mb-2">
              Duration (minutes)
            </label>
            <input
              id="duration"
              type="number"
              min="5"
              max="480"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              value={formData.suggested_duration}
              onChange={(e) => setFormData({ ...formData, suggested_duration: parseInt(e.target.value) || 60 })}
              disabled={disabled}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="personas" className="block text-sm font-medium text-gray-700 mb-2">
              Target Learner Roles
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
              <option value="architect">Solution Architect</option>
              <option value="operations">Operations Engineer</option>
              <option value="security">Security Engineer</option>
              <option value="data_engineer">Data Engineer</option>
              <option value="ml_engineer">ML Engineer</option>
              <option value="all_roles">All Roles</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
          </div>

          <div>
            <label htmlFor="sandbox_type" className="block text-sm font-medium text-gray-700 mb-2">
              Sandbox Environment
            </label>
            <select
              id="sandbox_type"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              value={formData.suggested_sandbox_type}
              onChange={(e) => setFormData({ ...formData, suggested_sandbox_type: e.target.value })}
              disabled={disabled}
            >
              <option value="individual">Individual - Single learner</option>
              <option value="shared">Shared - Multi-learner</option>
              <option value="isolated">Isolated - Completely separate</option>
              <option value="managed">Managed - Instructor controlled</option>
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-2">
            Topic Tags
          </label>
          <input
            id="tags"
            type="text"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="e.g., serverless, python, api-gateway, cloudformation"
            value={formData.suggested_tags?.join(', ') || ''}
            onChange={(e) => setFormData({ 
              ...formData, 
              suggested_tags: e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag)
            })}
            disabled={disabled}
          />
          <p className="text-xs text-gray-500 mt-1">Separate multiple tags with commas</p>
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