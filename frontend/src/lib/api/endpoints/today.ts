import { api } from '../client';
import type { FocusSessionPayload, TodayDraft, TodayPreviewResponse, TodayResponse } from '../types';

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

export const getTodayPlan = async (requestedDate?: string | null): Promise<TodayResponse> => {
  return await api.get(requestedDate ? `/today?date=${requestedDate}` : "/today");
};

export const completeTodayTask = async (taskId: string): Promise<void> => {
  await api.patch(`/today/tasks/${taskId}/status`, { status: "COMPLETED" });
};

export const replanToday = async (dateStr: string): Promise<TodayResponse> => {
  return await api.post(`/today/replan?target_date=${dateStr}`);
};

export const startFocusSession = async (payload: FocusSessionPayload): Promise<void> => {
  await api.post("/focus/start", payload);
};
