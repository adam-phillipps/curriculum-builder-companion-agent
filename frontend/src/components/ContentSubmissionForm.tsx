'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';
import { ContentSubmissionRequest, ContentSubmissionResponse } from '@/types/api';

interface SimilarContent {
  id: number;
  title: string;
  description: string;
  content_type: string;
  author?: string;
  created_at: string;
  similarity_score: number;
}

interface SimilaritySearchResponse {
  results: SimilarContent[];
  total_found: number;
  search_time_ms?: number;
}

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
    author: '',
    co_authors: '',
    sources: '',
    artifacts: '',
    ai_assisted: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [similarContent, setSimilarContent] = useState<SimilarContent[]>([]);
  const [checkingSimilarity, setCheckingSimilarity] = useState(false);
  const [showSimilarContent, setShowSimilarContent] = useState(false);
  const [similarityQuery, setSimilarityQuery] = useState('');

  const checkSimilarity = async () => {
    if (!similarityQuery.trim()) return;
    
    setCheckingSimilarity(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8001/api/v1/vector/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query_text: similarityQuery,
          similarity_threshold: 0.3,
          max_results: 10,
          search_approved_only: false
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data: SimilaritySearchResponse = await response.json();
      setSimilarContent(data.results);
      setShowSimilarContent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Similarity check failed');
    } finally {
      setCheckingSimilarity(false);
    }
  };
  
  const getSimilarityColor = (score: number) => {
    if (score >= 0.8) return 'text-red-600 bg-red-50 border-red-200';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-green-600 bg-green-50 border-green-200';
  };
  
  const getSimilarityWarning = (score: number) => {
    if (score >= 0.8) return 'High similarity detected - please review carefully';
    if (score >= 0.6) return 'Similar content found - please review before submitting';
    return 'Low similarity - content appears unique';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    onSubmissionStart();

    try {
      // Submit to the agentic workflow endpoint
      const response = await fetch('http://localhost:8001/api/v1/agents/process-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: formData.content,
          title: formData.title,
          model_provider: formData.model_provider,
          model_name: formData.model_name,
          suggested_tier: formData.suggested_tier,
          suggested_personas: formData.suggested_personas,
          suggested_content_type: formData.suggested_content_type,
          suggested_tags: formData.suggested_tags,
          suggested_duration: formData.suggested_duration,
          suggested_sandbox_type: formData.suggested_sandbox_type,
          author: formData.author,
          co_authors: formData.co_authors,
          sources: formData.sources,
          artifacts: formData.artifacts,
          ai_assisted: formData.ai_assisted
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
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



        {/* Similarity Search Section */}
        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Check for Similar Content</h3>
          <p className="text-sm text-gray-600 mb-3">
            Search for existing content similar to what you're planning to submit. This helps avoid duplicates.
          </p>
          
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Enter title, description, or key concepts to search for similar content..."
              value={similarityQuery}
              onChange={(e) => setSimilarityQuery(e.target.value)}
              disabled={disabled}
            />
            <button
              type="button"
              onClick={checkSimilarity}
              disabled={disabled || checkingSimilarity || !similarityQuery.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {checkingSimilarity ? 'Checking...' : 'Check Similarity'}
            </button>
          </div>
          
          {showSimilarContent && (
            <div className="mt-4">
              <h4 className="font-medium text-gray-900 mb-2">
                Found {similarContent.length} similar content items
              </h4>
              
              {similarContent.length === 0 ? (
                <p className="text-sm text-green-600 bg-green-50 border border-green-200 rounded-lg p-3">
                  ✅ No similar content found - your content appears to be unique!
                </p>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {similarContent.map((item) => (
                    <div key={item.id} className={`border rounded-lg p-3 ${getSimilarityColor(item.similarity_score)}`}>
                      <div className="flex justify-between items-start mb-2">
                        <h5 className="font-medium">{item.title}</h5>
                        <span className="text-sm font-medium">
                          {Math.round(item.similarity_score * 100)}% similar
                        </span>
                      </div>
                      <p className="text-sm mb-2">{item.description}</p>
                      <div className="flex justify-between text-xs">
                        <span>Type: {item.content_type}</span>
                        <span>Author: {item.author || 'Unknown'}</span>
                        <span>Created: {new Date(item.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                  
                  {similarContent.some(item => item.similarity_score >= 0.6) && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-3">
                      <p className="text-sm text-yellow-800">
                        ⚠️ {getSimilarityWarning(Math.max(...similarContent.map(item => item.similarity_score)))}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 gap-4">
          <div>
            <label htmlFor="author" className="block text-sm font-medium text-gray-700 mb-2">
              Author
            </label>
            <input
              id="author"
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., John Smith, jane.doe@company.com"
              value={formData.author || ''}
              onChange={(e) => setFormData({ ...formData, author: e.target.value })}
              disabled={disabled}
            />
          </div>

          <div>
            <label htmlFor="co_authors" className="block text-sm font-medium text-gray-700 mb-2">
              Co-Authors
            </label>
            <input
              id="co_authors"
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., Alice Johnson, Bob Wilson"
              value={formData.co_authors || ''}
              onChange={(e) => setFormData({ ...formData, co_authors: e.target.value })}
              disabled={disabled}
            />
            <p className="text-xs text-gray-500 mt-1">Separate multiple co-authors with commas</p>
          </div>

          <div>
            <label htmlFor="sources" className="block text-sm font-medium text-gray-700 mb-2">
              Sources & References
            </label>
            <textarea
              id="sources"
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., AWS Documentation, https://docs.aws.amazon.com/lambda/"
              value={formData.sources || ''}
              onChange={(e) => setFormData({ ...formData, sources: e.target.value })}
              disabled={disabled}
            />
            <p className="text-xs text-gray-500 mt-1">Links, documentation, or other reference materials</p>
          </div>

          <div>
            <label htmlFor="artifacts" className="block text-sm font-medium text-gray-700 mb-2">
              Additional Artifacts
            </label>
            <textarea
              id="artifacts"
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., https://youtube.com/watch?v=example, https://datasets.example.com/data.zip"
              value={formData.artifacts || ''}
              onChange={(e) => setFormData({ ...formData, artifacts: e.target.value })}
              disabled={disabled}
            />
            <p className="text-xs text-gray-500 mt-1">Links to videos, datasets, or other supplementary materials</p>
          </div>

          <div>
            <label htmlFor="ai_assisted" className="block text-sm font-medium text-gray-700 mb-2">
              AI Assistance Credit
            </label>
            <input
              id="ai_assisted"
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., ChatGPT-4, Claude 3.5, GitHub Copilot"
              value={formData.ai_assisted || ''}
              onChange={(e) => setFormData({ ...formData, ai_assisted: e.target.value })}
              disabled={disabled}
            />
            <p className="text-xs text-gray-500 mt-1">Credit AI tools used in content creation</p>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={disabled || !formData.content.trim()}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {disabled ? 'Processing with AI...' : 'Submit Content for AI Processing'}
        </button>
        
        <div className="text-xs text-gray-500 text-center mt-2">
          Content will be processed through our AI workflow for metadata extraction and similarity checking
        </div>
      </form>
    </div>
  );
}