import { PUBLIC_API_BASE_URL } from '$env/static/public';
import { browser } from '$app/environment';
import { isRetryableTransportFailure } from '$lib/shared/networkFailures';
import { recordServerDate } from '$lib/shared/serverClock';
export { serverNow } from '$lib/shared/serverClock';

export class APIError extends Error {
  public status: number;
  public detail: { detail?: unknown; message?: unknown } | null;

  constructor(status: number, detail: unknown) {
    let message = 'API Error';
    if (typeof detail === 'string') {
      message = detail;
    } else if (detail && typeof detail === 'object') {
      const body = detail as { detail?: unknown; message?: unknown };
      if (typeof body.detail === 'string') {
        message = body.detail;
      } else if (body.detail && typeof body.detail === 'object' && 'message' in body.detail && typeof body.detail.message === 'string') {
        message = body.detail.message;
      } else if (Array.isArray(body.detail) && body.detail.length > 0) {
        const issue = body.detail[0] as { msg?: unknown };
        message = typeof issue.msg === 'string' ? issue.msg : 'Validation Error';
      } else if (typeof body.message === 'string') {
        message = body.message;
      }
    }
    super(message);
    this.status = status;
    this.detail = detail && typeof detail === 'object'
      ? detail as { detail?: unknown; message?: unknown }
      : null;
    this.name = 'APIError';
  }
}

interface RequestOptions extends RequestInit {
  data?: any;
  formUrlEncoded?: boolean;
  /** Abort the request after this many milliseconds (0 disables the limit). */
  timeoutMs?: number;
}

const GET_RETRY_ATTEMPTS = 4;
const GET_RETRY_BASE_DELAY_MS = 500;
const GET_RETRY_MAX_DELAY_MS = 30_000;

function waitForRetry(delayMs: number, signal?: AbortSignal | null): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(new DOMException('Aborted', 'AbortError'));
    const timer = setTimeout(done, delayMs);
    const online = () => done();
    const abort = () => {
      cleanup();
      reject(new DOMException('Aborted', 'AbortError'));
    };
    function cleanup() {
      clearTimeout(timer);
      if (typeof window !== 'undefined') window.removeEventListener('online', online);
      signal?.removeEventListener('abort', abort);
    }
    function done() {
      cleanup();
      resolve();
    }
    if (typeof window !== 'undefined') window.addEventListener('online', online, { once: true });
    signal?.addEventListener('abort', abort, { once: true });
  });
}

/** A request that never answers must not leave the UI waiting forever. */
export const DEFAULT_REQUEST_TIMEOUT_MS = 30_000;
/** The assistant may call several models; the backend caps that chain at 45s. */
export const CHAT_REQUEST_TIMEOUT_MS = 75_000;
export const REQUEST_TIMEOUT_STATUS = 408;
const LONG_RUNNING_ENDPOINTS: Record<string, number> = {
  '/assistant/chat': CHAT_REQUEST_TIMEOUT_MS
};

type AuthErrorHandler = () => void;
let onAuthError: AuthErrorHandler | null = null;

export const setAuthErrorHandler = (handler: AuthErrorHandler) => {
  onAuthError = handler;
};

const TOKEN_KEY = 'blooming_access_token';

export const api = {
  async fetch(endpoint: string, options: RequestOptions = {}) {
    const { data, formUrlEncoded, timeoutMs: requestedTimeout, ...fetchOptions } = options;
    
    const headers = new Headers(fetchOptions.headers || {});
    
    if (browser) {
      const token = localStorage.getItem(TOKEN_KEY);
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
    }

    // Configuration owns the API prefix: PUBLIC_API_BASE_URL must already end
    // in /api/v1. Endpoint callers provide only resource paths such as
    // /auth/login or /me.
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
    const timeoutMs = requestedTimeout ?? LONG_RUNNING_ENDPOINTS[path] ?? DEFAULT_REQUEST_TIMEOUT_MS;

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
    
    const controller = new AbortController();
    let timedOut = false;
    const callerSignal = fetchOptions.signal;
    const forwardAbort = () => controller.abort();
    if (callerSignal) {
      if (callerSignal.aborted) controller.abort();
      else callerSignal.addEventListener('abort', forwardAbort, { once: true });
    }
    const timer = timeoutMs > 0
      ? setTimeout(() => { timedOut = true; controller.abort(); }, timeoutMs)
      : undefined;

    let response: Response;
    try {
      response = await fetch(urlStr, {
        ...fetchOptions,
        headers,
        signal: controller.signal
      });
      recordServerDate(response.headers?.get?.('Date') ?? null);
    } catch (error) {
      if (timedOut) {
        throw new APIError(REQUEST_TIMEOUT_STATUS, 'The server took too long to respond. Please try again.');
      }
      throw error;
    } finally {
      if (timer) clearTimeout(timer);
      callerSignal?.removeEventListener('abort', forwardAbort);
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

  async get(endpoint: string, options?: Omit<RequestOptions, 'method' | 'data' | 'formUrlEncoded'>) {
    for (let attempt = 0; ; attempt += 1) {
      try {
        return await this.fetch(endpoint, { ...options, method: 'GET' });
      } catch (error) {
        if (attempt >= GET_RETRY_ATTEMPTS - 1 || !isRetryableTransportFailure(error)) throw error;
        const exponential = Math.min(GET_RETRY_MAX_DELAY_MS, GET_RETRY_BASE_DELAY_MS * 2 ** attempt);
        const jittered = Math.round(exponential * (0.75 + Math.random() * 0.5));
        await waitForRetry(jittered, options?.signal);
      }
    }
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






