import { PUBLIC_API_BASE_URL } from '$env/static/public';
import { browser } from '$app/environment';

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
  schedulingType: 'FLEXIBLE' | 'FIXED';
  importance: 'CORE' | 'OPTIONAL';
  estimateSource: 'USER' | 'RULE' | 'AI' | 'HISTORY';
  category?: string | null;
  fixedStart?: string | null;
  fixedEnd?: string | null;
  deadline?: string | null;
  dependencies: string[];
  splittable: boolean;
  breakAfterMin?: number | null;
  /** Saving creates a repeating template for this task. */
  recurrence?: RecurrenceDraft | null;
  /** Server-issued: the repeating template this task is an occurrence of. */
  recurringTaskId?: string | null;
  /** Server-issued: an existing unscheduled task carried into this day. */
  sourceTaskId?: string | null;
}

export interface RecurrenceDraft {
  freq: 'DAILY' | 'WEEKLY';
  /** 0 = Monday ... 6 = Sunday. */
  weekdays?: number[];
  until?: string | null;
}

export interface DeferredTaskDraft {
  task: TaskDraft;
  targetDate: string;
}

export interface TodayDraft {
  type: 'today';
  planDate: string;
  timezone: string;
  windows: { start: string; end: string }[];
  tasks: TaskDraft[];
  deferred_tasks?: DeferredTaskDraft[];
}

export interface MilestoneDraft {
  id?: string | null;
  title: string;
  targetDate: string;
  expectedOutcome?: string | null;
}

export interface RoadmapDraft {
  type: 'roadmap';
  goalId?: string | null;
  goalTitle: string;
  goalDescription: string;
  targetDate: string;
  milestones: MilestoneDraft[];
}

export type AssistantDraft = TodayDraft | RoadmapDraft;

export type PatchOp = 
  | { op: "remove_task"; task_id: string }
  | { op: "remove_deferred_task"; task_id: string }
  | { op: "move_task_to_date"; task_id: string; target_date: string; timezone?: string | null }
  | { op: "update_window"; window_index: number; start?: string | null; end?: string | null }
  | { op: "update_task"; task_id: string; duration_min?: number | null; title?: string | null; importance?: "CORE" | "OPTIONAL" | null; priority?: "LOW" | "MEDIUM" | "HIGH" | "URGENT" | null; category?: "Learning" | "Work" | "Personal" | null; break_after_min?: number | null; splittable?: boolean | null; fixed_start?: string | null; fixed_end?: string | null; deadline?: string | null; scheduling_type?: "FLEXIBLE" | "FIXED" | null }
  | { op: "split_task"; task_id: string; split_minutes: number }
  | { op: "add_task"; task: TaskDraft }
  | { op: "scale_durations"; factor: number; task_id?: string | null }
  | { op: "set_windows"; windows: AvailabilityWindowDraft[] }
  | { op: "set_plan_date"; plan_date: string };

export interface RepairSuggestion {
  label: string;
  patch: PatchOp[];
}

export interface AssistantSuggestion {
  label: string;
  action?: string | null;
  send_text?: string | null;
  patch?: PatchOp[] | null;
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
  structured_payload: {
    draft?: AssistantDraft | null;
    preview?: TodayPreviewResponse | null;
    degraded?: string | null;
    suggestions?: AssistantSuggestion[];
    assumptions?: AssistantAssumption[];
  } | null;
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
  suggestions?: RepairSuggestion[];
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
    session_id: sessionId, preview_token: previewToken, idempotency_key: previewToken,
    draft, replace_existing: replaceExisting
  });
};

export const saveRoadmap = async (
  sessionId: string | null, draft: RoadmapDraft, idempotencyKey: string
): Promise<unknown> => {
  if (draft.goalId) {
    return await api.put(`/goals/${draft.goalId}/from-roadmap`, {
      session_id: sessionId,
      idempotency_key: idempotencyKey,
      draft
    });
  }
  return await api.post('/goals/from-roadmap', {
    session_id: sessionId,
    idempotency_key: idempotencyKey,
    draft
  });
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
