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






export interface AvailabilityWindowDraft {
  start: string;
  end: string;
}

export interface TaskDraft {
  id: string;
  title: string;
  durationMin: number;
  priority: 'URGENT' | 'HIGH' | 'MEDIUM' | 'LOW';
  importance: 'CORE' | 'OPTIONAL';
  category: string | null;
  estimateSource: 'USER' | 'RULE' | 'AI' | 'HISTORY';
  breakAfterMin: number | null;
  deadline: string | null;
  schedulingType: 'FLEXIBLE' | 'FIXED';
  fixedStart: string | null;
  fixedEnd: string | null;
  dependencies: string[];
  splittable: boolean;
}

export interface TodayDraft {
  type: 'today';
  planDate: string;
  timezone: string;
  windows: AvailabilityWindowDraft[];
  tasks: TaskDraft[];
}

export interface MilestoneDraft {
  id?: string | null;
  title: string;
  targetDate: string;
  expectedOutcome?: string | null;
}

export interface RoadmapDraft {
  type: 'roadmap';
  goalTitle: string;
  goalDescription: string;
  targetDate: string;
  milestones: MilestoneDraft[];
}

export type AssistantDraft = TodayDraft | RoadmapDraft;

export interface AssistantSuggestion {
  label: string;
  action?: string | null;
  send_text?: string | null;
  patch?: Record<string, unknown>[] | null;
}

export interface AssistantAssumption {
  id: string;
  kind: string;
  text: string;
  task_id: string | null;
}

export interface AssistantSessionMessage {
  role: 'user' | 'assistant';
  content: string;
  structured_payload: Record<string, any> | null;
  created_at: string;
}

export interface AssistantSession {
  session_id: string;
  status: string;
  messages: AssistantSessionMessage[];
}


export interface TodayBlock {
  id: string;
  block_type: string;
  task_id: string | null;
  draft_task_id: string | null;
  title: string | null;
  description: string | null;
  category: string | null;
  estimated_duration_minutes: number | null;
  importance: 'CORE' | 'OPTIONAL' | null;
  preferred_break_duration_minutes: number | null;
  source: string | null;
  planned_start_at: string;
  planned_end_at: string;
  position: number;
  status: string;
  is_locked: boolean;
}

export interface UnscheduledTask {
  draft_task_id: string | null;
  title: string;
  reason: string;
}

export interface UnscheduledReason {
  code: string;
  task_id: string;
  dependency_id?: string;
}

export interface TodayResponse {
  plan_date: string;
  status: string;
  timezone: string;
  unscheduled_tasks: UnscheduledTask[] | string[];
  reasons: UnscheduledReason[];
  reality_check: string | null;
  blocks: TodayBlock[];
}

export interface TodayPreviewResponse extends TodayResponse {
  preview_token: string;
}

export const previewTodayPlan = async (draft: TodayDraft): Promise<TodayPreviewResponse> => {
  return await api.post('/today/preview', { draft });
};

export const saveTodayPlan = async (
  sessionId: string | null, previewToken: string, draft: TodayDraft, replaceExisting = false
): Promise<TodayResponse> => {
  return await api.post('/today/save', {
    session_id: sessionId, preview_token: previewToken, draft, replace_existing: replaceExisting
  });
};

export const saveRoadmap = async (sessionId: string | null, draft: RoadmapDraft): Promise<any> => {
  return await api.post('/goals/from-roadmap', { session_id: sessionId, draft });
};

export interface ChatResponse {
  reply: string;
  session_id: string | null;
  intent: string | null;
  tier: string;
  degraded: string | null;
  draft: AssistantDraft | null;
  preview: TodayPreviewResponse | null;
  goal_created: Record<string, unknown> | null;
  suggestions: AssistantSuggestion[];
  assumptions: AssistantAssumption[];
  question: string | null;
}
