import { PUBLIC_API_BASE_URL } from '$env/static/public';
import { browser } from '$app/environment';

export class APIError extends Error {
  public status: number;
  public detail: any;

  constructor(status: number, detail: any) {
    let message = 'API Error';
    if (typeof detail === 'string') {
      message = detail;
    } else if (detail && typeof detail === 'object') {
      if (typeof detail.detail === 'string') {
        message = detail.detail;
      } else if (Array.isArray(detail.detail) && detail.detail.length > 0) {
        message = detail.detail[0].msg || 'Validation Error';
      } else if (detail.message) {
        message = detail.message;
      }
    }
    super(message);
    this.status = status;
    this.detail = detail;
    this.name = 'APIError';
  }
}

interface RequestOptions extends RequestInit {
  data?: any;
  formUrlEncoded?: boolean;
}

type AuthErrorHandler = () => void;
let onAuthError: AuthErrorHandler | null = null;

export const setAuthErrorHandler = (handler: AuthErrorHandler) => {
  onAuthError = handler;
};

const TOKEN_KEY = 'blooming_access_token';

export const api = {
  async fetch(endpoint: string, options: RequestOptions = {}) {
    const { data, formUrlEncoded, ...fetchOptions } = options;
    
    const headers = new Headers(fetchOptions.headers || {});
    
    if (browser) {
      const token = localStorage.getItem(TOKEN_KEY);
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
    }

    let urlStr = PUBLIC_API_BASE_URL;
    if (urlStr.endsWith('/')) {
      urlStr = urlStr.slice(0, -1);
    }
    
    let path = endpoint;
    // Prefix removal, if retained for backward compatibility, must only match complete path segments
    if (path.startsWith('/api/v1/')) {
      path = path.replace('/api/v1', '');
    } else if (path.startsWith('/v1/')) {
      path = path.replace('/v1', '');
    } else if (path.startsWith('/api/')) {
      path = path.replace('/api', '');
    }
    if (!path.startsWith('/')) {
      path = `/${path}`;
    }
    urlStr += path;

    if (data) {
      if (formUrlEncoded) {
        headers.set('Content-Type', 'application/x-www-form-urlencoded');
        const params = new URLSearchParams();
        for (const key in data) {
          params.append(key, data[key]);
        }
        fetchOptions.body = params.toString();
      } else {
        headers.set('Content-Type', 'application/json');
        fetchOptions.body = JSON.stringify(data);
      }
    }
    
    const response = await fetch(urlStr, {
      ...fetchOptions,
      headers
    });

    // For 204 No Content, don't try to parse JSON
    if (response.status === 204) {
      return null;
    }

    let responseData;
    try {
      responseData = await response.json();
    } catch (e) {
      // If we can't parse JSON and it's not ok, we still throw an error
      if (!response.ok) {
        if (response.status === 401 && onAuthError && !endpoint.includes('/auth/login')) {
          onAuthError();
        }
        throw new APIError(response.status, response.statusText);
      }
      return null;
    }

    if (!response.ok) {
      if (response.status === 401 && onAuthError && !endpoint.includes('/auth/login')) {
        onAuthError();
      }
      throw new APIError(response.status, responseData);
    }

    return responseData;
  },

  get(endpoint: string, options?: Omit<RequestOptions, 'method' | 'data' | 'formUrlEncoded'>) {
    return this.fetch(endpoint, { ...options, method: 'GET' });
  },

  post(endpoint: string, data?: any, options?: Omit<RequestOptions, 'method' | 'data'>) {
    return this.fetch(endpoint, { ...options, method: 'POST', data });
  },
  
  put(endpoint: string, data?: any, options?: Omit<RequestOptions, 'method' | 'data'>) {
    return this.fetch(endpoint, { ...options, method: 'PUT', data });
  },
  
  patch(endpoint: string, data?: any, options?: Omit<RequestOptions, 'method' | 'data'>) {
    return this.fetch(endpoint, { ...options, method: 'PATCH', data });
  },
  
  delete(endpoint: string, options?: Omit<RequestOptions, 'method' | 'data' | 'formUrlEncoded'>) {
    return this.fetch(endpoint, { ...options, method: 'DELETE' });
  }
};
