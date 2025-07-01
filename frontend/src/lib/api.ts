// API client with proper error handling for Docker environment
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:8001/api';

export class ApiClient {
  private static async makeRequest(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error - please check your connection');
      }
      throw error;
    }
  }

  static async searchContent(params: {
    query_text?: string;
    metadata_filters?: Record<string, any>;
    similarity_threshold?: number;
    max_results?: number;
    search_approved_only?: boolean;
  }) {
    return this.makeRequest('/v1/vector/search', {
      method: 'POST',
      body: JSON.stringify({
        query_text: '',
        similarity_threshold: 0.1,
        max_results: 20,
        search_approved_only: false,
        ...params,
      }),
    });
  }

  static async getContent(contentId: number) {
    return this.makeRequest(`/v1/content/${contentId}`);
  }

  static async submitContent(data: any) {
    return this.makeRequest('/v1/agents/process-content', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// Export lowercase instance for compatibility
export const apiClient = ApiClient;