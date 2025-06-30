import { ContentSubmissionRequest, ContentSubmissionResponse, LearningContent } from '@/types/api';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
  : 'http://localhost:8001';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  // Agent endpoints
  async submitContent(data: ContentSubmissionRequest): Promise<ContentSubmissionResponse> {
    return this.request<ContentSubmissionResponse>('/api/v1/agents/process-content', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Content endpoints
  async getContent(): Promise<LearningContent[]> {
    return this.request<LearningContent[]>('/api/v1/content/');
  }

  async getContentById(id: number): Promise<LearningContent> {
    return this.request<LearningContent>(`/api/v1/content/${id}`);
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/health');
  }
}

export const apiClient = new ApiClient();