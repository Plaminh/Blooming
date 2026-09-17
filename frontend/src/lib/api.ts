import { PUBLIC_API_BASE_URL } from '$env/static/public';
import { get } from 'svelte/store';
import { authStore } from './shared/stores/authStore';

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

export const api = {
  async fetch(endpoint: string, options: RequestOptions = {}) {
    const { data, formUrlEncoded, ...fetchOptions } = options;
    
    const headers = new Headers(fetchOptions.headers || {});
    
    // Add Bearer token if we have one in the store
    const store = get(authStore);
    if (store.token) {
      headers.set('Authorization', `Bearer ${store.token}`);
    }

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

    const url = `${PUBLIC_API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      ...fetchOptions,
      headers
    });

    if (response.status === 401) {
      authStore.clearAuth();
    }

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
         throw new APIError(response.status, response.statusText);
      }
      return null;
    }

    if (!response.ok) {
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
  
  delete(endpoint: string, options?: Omit<RequestOptions, 'method' | 'data' | 'formUrlEncoded'>) {
    return this.fetch(endpoint, { ...options, method: 'DELETE' });
  }
};
