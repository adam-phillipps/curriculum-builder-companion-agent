'use client';

import { useState } from 'react';
import { X, Check, AlertTriangle, Edit3 } from 'lucide-react';
import { ContentSubmissionResponse } from '@/types/api';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  result: ContentSubmissionResponse;
  onApprove: (contentId: number) => void;
  onReject: (contentId: number, reason: string) => void;
  onEdit: (contentId: number, updatedMetadata: any) => void;
}

export default function ContentReviewModal({ isOpen, onClose, result, onApprove, onReject, onEdit }: Props) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedMetadata, setEditedMetadata] = useState(result.extracted_metadata);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectForm, setShowRejectForm] = useState(false);

  if (!isOpen) return null;

  const handleSaveEdit = () => {
    if (result.content_id) {
      onEdit(result.content_id, editedMetadata);
      setIsEditing(false);
    }
  };

  const handleReject = () => {
    if (result.content_id && rejectReason.trim()) {
      onReject(result.content_id, rejectReason);
      setShowRejectForm(false);
      onClose();
    }
  };

  const handleApprove = () => {
    if (result.content_id) {
      onApprove(result.content_id);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-6 h-6 text-orange-500" />
            <h2 className="text-xl font-semibold">Content Review Required</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Similar Content Warning */}
          {result.similar_content.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="font-medium text-yellow-800 mb-3">
                ⚠️ Similar Content Detected ({result.similar_content.length} items)
              </h3>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {result.similar_content.map((item, index) => (
                  <div key={index} className="bg-white p-3 rounded border text-sm">
                    <div className="font-medium">{item.title}</div>
                    <div className="text-gray-600">
                      {item.tier} • {item.content_type} • 
                      <span className="font-medium text-yellow-700">
                        {Math.round(item.similarity_score * 100)}% similar
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Metadata Editor */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-gray-800">Content Metadata</h3>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="btn-secondary text-sm"
              >
                <Edit3 className="w-4 h-4 mr-1" />
                {isEditing ? 'Cancel Edit' : 'Edit'}
              </button>
            </div>

            {isEditing ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    value={editedMetadata.title || ''}
                    onChange={(e) => setEditedMetadata({...editedMetadata, title: e.target.value})}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    value={editedMetadata.description || ''}
                    onChange={(e) => setEditedMetadata({...editedMetadata, description: e.target.value})}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Tier</label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      value={editedMetadata.tier || ''}
                      onChange={(e) => setEditedMetadata({...editedMetadata, tier: e.target.value})}
                    >
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
                      value={editedMetadata.content_type || ''}
                      onChange={(e) => setEditedMetadata({...editedMetadata, content_type: e.target.value})}
                    >
                      <option value="lesson">Lesson</option>
                      <option value="module">Module</option>
                      <option value="exercise">Exercise</option>
                      <option value="assessment">Assessment</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Duration (minutes)</label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    value={editedMetadata.estimated_duration || ''}
                    onChange={(e) => setEditedMetadata({...editedMetadata, estimated_duration: parseInt(e.target.value)})}
                  />
                </div>

                <button onClick={handleSaveEdit} className="btn-primary">
                  Save Changes
                </button>
              </div>
            ) : (
              <div className="space-y-2 text-sm">
                <div><span className="font-medium">Title:</span> {editedMetadata.title}</div>
                <div><span className="font-medium">Description:</span> {editedMetadata.description}</div>
                <div><span className="font-medium">Tier:</span> {editedMetadata.tier}</div>
                <div><span className="font-medium">Type:</span> {editedMetadata.content_type}</div>
                <div><span className="font-medium">Duration:</span> {editedMetadata.estimated_duration} minutes</div>
                {editedMetadata.aws_services && editedMetadata.aws_services.length > 0 && (
                  <div><span className="font-medium">AWS Services:</span> {editedMetadata.aws_services.join(', ')}</div>
                )}
              </div>
            )}
          </div>

          {/* Reject Form */}
          {showRejectForm && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h3 className="font-medium text-red-800 mb-3">Rejection Reason</h3>
              <textarea
                rows={3}
                className="w-full px-3 py-2 border border-red-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                placeholder="Please provide a reason for rejecting this content..."
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
              />
              <div className="flex space-x-3 mt-3">
                <button onClick={handleReject} className="btn-primary bg-red-600 hover:bg-red-700">
                  Confirm Rejection
                </button>
                <button onClick={() => setShowRejectForm(false)} className="btn-secondary">
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <button
              onClick={() => setShowRejectForm(true)}
              className="btn-secondary text-red-600 hover:bg-red-50"
            >
              Reject Content
            </button>
            <button
              onClick={handleApprove}
              className="btn-primary bg-green-600 hover:bg-green-700"
            >
              <Check className="w-4 h-4 mr-1" />
              Approve & Publish
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}