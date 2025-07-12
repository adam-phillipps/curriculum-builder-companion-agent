import { buildApiUrl } from '../config/api';

// API client with proper error handling for Docker environment

export class ApiClient {
  static async makeRequest(endpoint: string, options: RequestInit = {}) {
    const url = buildApiUrl(endpoint);
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      console.log('API Request:', url, defaultOptions);
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', response.status, response.statusText, errorText);
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('API Response:', data);
      return data;
    } catch (error) {
      console.error('API Request failed:', error);
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
    return this.makeRequest('vector/search', {
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
    return this.makeRequest(`content/${contentId}`);
  }

  static async getContentList(params: {
    limit?: number;
    offset?: number;
  } = {}) {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.offset) queryParams.append('offset', params.offset.toString());
    
    const queryString = queryParams.toString();
    const endpoint = queryString ? `content?${queryString}` : 'content';
    
    return this.makeRequest(endpoint);
  }

  static async submitContent(data: any) {
    return this.makeRequest('agents/process-content', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // User API methods
  static async getUsers() {
    return this.makeRequest('users/');
  }

  static async getAvailableRoles() {
    return this.makeRequest('users/roles/available');
  }

  static async signInUser(userId: number) {
    return this.makeRequest('users/sign-in', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    });
  }

  static async getLearnerProfile(userId: number) {
    return this.makeRequest(`users/${userId}/learner-profile`);
  }

  static async getUserContentProgress(userId: number) {
    return this.makeRequest(`users/${userId}/content-progress`);
  }
}

// Simple API wrapper for easier usage
export const api = {
  get: async (endpoint: string) => {
    const data = await ApiClient.makeRequest(endpoint);
    return { data };
  },
  post: async (endpoint: string, data?: any) => {
    const result = await ApiClient.makeRequest(endpoint, { 
      method: 'POST', 
      body: data ? JSON.stringify(data) : undefined 
    });
    return { data: result };
  },
};

// Export lowercase instance for compatibility
export const apiClient = ApiClient;