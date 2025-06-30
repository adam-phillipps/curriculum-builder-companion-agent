'use client';

import { useState } from 'react';
import ContentSubmissionForm from '@/components/ContentSubmissionForm';
import WorkflowProgress from '@/components/WorkflowProgress';
import { ContentSubmissionResponse } from '@/types/api';

export default function HomePage() {
  const [workflowResult, setWorkflowResult] = useState<ContentSubmissionResponse | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmissionComplete = (result: ContentSubmissionResponse) => {
    setWorkflowResult(result);
    setIsProcessing(false);
  };

  const handleSubmissionStart = () => {
    setIsProcessing(true);
    setWorkflowResult(null);
  };

  const handleReset = () => {
    setWorkflowResult(null);
    setIsProcessing(false);
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          AI-Powered Curriculum Builder
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Submit your learning content and let our AI agents extract metadata, 
          check for similarities, and create structured curriculum materials.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <ContentSubmissionForm
            onSubmissionStart={handleSubmissionStart}
            onSubmissionComplete={handleSubmissionComplete}
            disabled={isProcessing}
          />
        </div>
        
        <div>
          <WorkflowProgress
            result={workflowResult}
            isProcessing={isProcessing}
            onReset={handleReset}
          />
        </div>
      </div>
    </div>
  );
}