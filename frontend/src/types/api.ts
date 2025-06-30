// API Types matching our FastAPI backend
export interface ContentSubmissionRequest {
  content: string;
  model_provider?: string;
  model_name?: string;
  suggested_tier?: string;
  suggested_personas?: string[];
  suggested_content_type?: string;
}

export interface ContentSubmissionResponse {
  workflow_id: string;
  status: string;
  content_id?: number;
  extracted_metadata: Record<string, any>;
  similar_content: Array<{
    id: number;
    title: string;
    similarity_score: number;
    tier: string;
    content_type: string;
  }>;
  similarity_score?: number;
  human_review_required: boolean;
  error_message?: string;
}

export interface LearningContent {
  id: number;
  code_title: string;
  title: string;
  description: string;
  content_type: string;
  tier: string;
  personas: string[];
  learning_objectives: string[];
  estimated_duration: number;
  sandbox_type: string;
  aws_services: string[];
  technical_requirements: Record<string, any>;
  estimated_cost: number;
  status: string;
  created_at: string;
  updated_at: string;
}