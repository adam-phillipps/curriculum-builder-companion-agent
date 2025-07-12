'use client';

import { X } from 'lucide-react';
import { useState, useEffect } from 'react';
import { buildApiUrl } from '../../config/api';

interface User {
  id: number;
  first_name?: string;
  last_name?: string;
  current_role: string;
}

interface ContentPreviewModalProps {
  content: {
    id: number;
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
  currentUser?: User | null;
}

export default function ContentPreviewModal({ 
  content, 
  isOpen, 
  onClose, 
  onViewContent,
  currentUser 
}: ContentPreviewModalProps) {
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [comprehension, setComprehension] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Check enrollment status when modal opens
  useEffect(() => {
    if (isOpen && currentUser && content.id) {
      checkEnrollmentStatus();
    }
  }, [isOpen, currentUser, content.id]);
  
  const checkEnrollmentStatus = async () => {
    if (!currentUser) return;
    
    try {
      const response = await fetch(buildApiUrl(`progress/${currentUser.id}/${content.id}`));
      if (response.ok) {
        const progress = await response.json();
        setIsEnrolled(true);
        setComprehension(progress.comprehension_percentage || 0);
        setIsCompleted(progress.status === 'completed');
      }
    } catch (error) {
      // Not enrolled yet
      setIsEnrolled(false);
    }
  };
  
  const handleEnroll = async () => {
    if (!currentUser) return;
    
    setLoading(true);
    try {
      const response = await fetch(buildApiUrl('progress/enroll'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUser.id,
          content_id: content.id
        })
      });
      
      if (response.ok) {
        setIsEnrolled(true);
        setComprehension(0);
      }
    } catch (error) {
      console.error('Enrollment failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleComprehensionChange = async (value: number) => {
    if (!currentUser || !isEnrolled) return;
    
    setComprehension(value);
    
    try {
      await fetch(buildApiUrl('progress/update'), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUser.id,
          content_id: content.id,
          comprehension_percentage: value
        })
      });
    } catch (error) {
      console.error('Failed to update comprehension:', error);
    }
  };
  
  const handleMarkComplete = async () => {
    if (!currentUser || !isEnrolled) return;
    
    setLoading(true);
    try {
      const response = await fetch(buildApiUrl('progress/update'), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUser.id,
          content_id: content.id,
          status: 'completed'
        })
      });
      
      if (response.ok) {
        setIsCompleted(true);
      }
    } catch (error) {
      console.error('Failed to mark complete:', error);
    } finally {
      setLoading(false);
    }
  };
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
              <span className="ml-2 text-gray-700">{content.id}</span>
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
        <div className="p-6 border-t bg-gray-50">
          {/* Comprehension Slider - Only show if enrolled */}
          {isEnrolled && currentUser && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                How comfortable are you with this material? ({Math.round(comprehension)}%)
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={comprehension}
                onChange={(e) => handleComprehensionChange(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Not comfortable</span>
                <span>Very comfortable</span>
              </div>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {/* Enroll Button - Only show if not enrolled and user is logged in */}
              {!isEnrolled && currentUser && (
                <button
                  onClick={handleEnroll}
                  disabled={loading}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Enrolling...' : 'Enroll'}
                </button>
              )}
              
              {/* Mark Complete Button - Only show if enrolled but not completed */}
              {isEnrolled && !isCompleted && currentUser && (
                <button
                  onClick={handleMarkComplete}
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Updating...' : 'Mark Complete'}
                </button>
              )}
              
              {/* Completed Status */}
              {isCompleted && (
                <span className="px-4 py-2 bg-green-100 text-green-800 rounded-lg font-medium">
                  ✓ Completed
                </span>
              )}
            </div>
            
            <div className="flex items-center space-x-3">
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
      </div>
    </div>
  );
}