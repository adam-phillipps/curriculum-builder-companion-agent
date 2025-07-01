'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import ContentSubmissionForm from './ContentSubmissionForm';
import WorkflowProgress from './WorkflowProgress';
import ContentSearch from './ContentSearch';
import ContentReviewModal from './ContentReviewModal';
import ContentManagement from './ContentManagement/ContentManagement';
import { ContentSubmissionResponse } from '@/types/api';

export default function ContentDashboard() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [workflowResult, setWorkflowResult] = useState<ContentSubmissionResponse | null>(null);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewContent, setReviewContent] = useState<ContentSubmissionResponse | null>(null);

  const handleSubmissionStart = () => {
    setIsProcessing(true);
    setWorkflowResult(null);
  };

  const handleSubmissionComplete = (result: ContentSubmissionResponse) => {
    setIsProcessing(false);
    setWorkflowResult(result);
  };

  const handleReset = () => {
    setWorkflowResult(null);
    setIsProcessing(false);
  };

  const handleReviewContent = (result: ContentSubmissionResponse) => {
    setReviewContent(result);
    setShowReviewModal(true);
  };

  const handleQuickApprove = async (contentId: number) => {
    try {
      // TODO: Implement quick approve API call
      console.log('Quick approving content:', contentId);
      // For now, just update the UI
      if (workflowResult) {
        setWorkflowResult({
          ...workflowResult,
          status: 'published',
          human_review_required: false
        });
      }
    } catch (error) {
      console.error('Quick approve failed:', error);
    }
  };

  const handleApproveContent = async (contentId: number) => {
    try {
      // TODO: Implement approve API call
      console.log('Approving content:', contentId);
      setShowReviewModal(false);
      if (workflowResult) {
        setWorkflowResult({
          ...workflowResult,
          status: 'published',
          human_review_required: false
        });
      }
    } catch (error) {
      console.error('Approve failed:', error);
    }
  };

  const handleRejectContent = async (contentId: number, reason: string) => {
    try {
      // TODO: Implement reject API call
      console.log('Rejecting content:', contentId, 'Reason:', reason);
      setShowReviewModal(false);
      if (workflowResult) {
        setWorkflowResult({
          ...workflowResult,
          status: 'error',
          error_message: `Content rejected: ${reason}`
        });
      }
    } catch (error) {
      console.error('Reject failed:', error);
    }
  };

  const handleEditContent = async (contentId: number, updatedMetadata: any) => {
    try {
      // TODO: Implement edit API call
      console.log('Editing content:', contentId, 'Updated metadata:', updatedMetadata);
      if (workflowResult) {
        setWorkflowResult({
          ...workflowResult,
          extracted_metadata: updatedMetadata
        });
      }
    } catch (error) {
      console.error('Edit failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Curriculum Builder Companion
          </h1>
          <p className="text-gray-600">
            AI-powered content creation and similarity detection for learning materials
          </p>
        </div>

        <Tabs defaultValue="submit" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="submit">Submit Content</TabsTrigger>
            <TabsTrigger value="search">Search Content</TabsTrigger>
            <TabsTrigger value="manage">Manage Content</TabsTrigger>
          </TabsList>

          <TabsContent value="submit" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ContentSubmissionForm
                onSubmissionStart={handleSubmissionStart}
                onSubmissionComplete={handleSubmissionComplete}
                disabled={isProcessing}
              />
              <WorkflowProgress
                result={workflowResult}
                isProcessing={isProcessing}
                onReset={handleReset}
                onReviewContent={handleReviewContent}
                onQuickApprove={handleQuickApprove}
              />
            </div>
          </TabsContent>

          <TabsContent value="search">
            <ContentSearch />
          </TabsContent>

          <TabsContent value="manage">
            <ContentManagement />
          </TabsContent>
        </Tabs>

        {/* Review Modal */}
        {showReviewModal && reviewContent && (
          <ContentReviewModal
            isOpen={showReviewModal}
            onClose={() => setShowReviewModal(false)}
            result={reviewContent}
            onApprove={handleApproveContent}
            onReject={handleRejectContent}
            onEdit={handleEditContent}
          />
        )}
      </div>
    </div>
  );
}