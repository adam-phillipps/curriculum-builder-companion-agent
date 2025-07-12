// API configuration - single source of truth
const getApiBaseUrl = (): string => {
  // In Next.js, NEXT_PUBLIC_ variables are available in browser
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // Fallback for development
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8001';
  }
  
  // Production fallback (should not happen if env var is set)
  throw new Error('API_URL not configured');
};

const getDocsBaseUrl = (): string => {
  if (process.env.NEXT_PUBLIC_DOCS_URL) {
    return process.env.NEXT_PUBLIC_DOCS_URL;
  }
  
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8080';
  }
  
  // Production fallback - assume docs are served from same domain
  return '';
};

export const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  API_VERSION: '/api/v1',
  DOCS_BASE_URL: getDocsBaseUrl(),
  get FULL_BASE_URL() {
    return `${this.BASE_URL}${this.API_VERSION}`;
  }
};

// Helper function for building API URLs
export const buildApiUrl = (endpoint: string): string => {
  // Remove leading slash if present to avoid double slashes
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${API_CONFIG.FULL_BASE_URL}/${cleanEndpoint}`;
};

// Helper function for building docs URLs
export const buildDocsUrl = (path: string): string => {
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${API_CONFIG.DOCS_BASE_URL}/${cleanPath}`;
};