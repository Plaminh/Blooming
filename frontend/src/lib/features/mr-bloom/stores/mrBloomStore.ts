import { writable } from 'svelte/store';
import {
  api, APIError, previewTodayPlan, saveTodayPlan,
  type TodayDraft, type RoadmapDraft, type TaskDraft, type MilestoneDraft,
  type AssistantDraft, type TodayPreviewResponse, type AssistantSuggestion,
  type AssistantAssumption, type AssistantSession, saveRoadmap, type ChatResponse
} from '$lib/api';
import type { IconName } from '$lib/shared/components/atoms/AppIcon.svelte';

export type { TodayDraft, RoadmapDraft } from '$lib/api';
export type DraftTask = TaskDraft;
export type Milestone = MilestoneDraft;
export type MessageRole = 'user' | 'assistant';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  status?: 'failed';
}

export type Importance = TaskDraft['importance'];
export interface TimelineEntry {
  id: string; type: 'task' | 'break' | 'buffer'; title: string;
  startTime: string; endTime: string; durationLabel: string;
  taskId?: string; icon?: IconName;
}
export type ActiveDraft = RoadmapDraft | TodayDraft | null;
export type PreviewMode = 'placeholder' | 'roadmap' | 'today' | 'timeline';

export interface MrBloomState {
  chatHistory: ChatMessage[];
  isWaitingForResponse: boolean;
  activeDraft: ActiveDraft;
  preview: TodayPreviewResponse | null;
  previewMode: PreviewMode;
  sessionId: string | null;
  degraded: string | null;
  suggestions: AssistantSuggestion[];
  assumptions: AssistantAssumption[];
  needsReplace: boolean;
  error?: string | null;
}

function timeLabel() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

let latestRequestVersion = 0;

async function sendMessage(
  message: string, msgId: string,
  update: (updater: (state: MrBloomState) => MrBloomState) => void,
  snapshot: MrBloomState
) {
  const version = ++latestRequestVersion;
  try {
    const result: ChatResponse = await api.post('/assistant/chat', {
      message, session_id: snapshot.sessionId, current_draft: snapshot.activeDraft
    });
    if (version !== latestRequestVersion) return;
    update(state => ({
      ...state, isWaitingForResponse: false,
      activeDraft: result.draft ?? state.activeDraft,
      preview: result.preview ?? (result.draft?.type === 'today' ? null : state.preview),
      previewMode: result.draft?.type ?? state.previewMode,
      sessionId: result.session_id ?? state.sessionId,
      degraded: result.degraded ?? null,
      suggestions: result.suggestions ?? [],
      assumptions: result.assumptions ?? [],
      chatHistory: [...state.chatHistory, {
        id: crypto.randomUUID(), role: 'assistant', content: result.reply, timestamp: timeLabel()
      }]
    }));
  } catch (error) {
    if (version !== latestRequestVersion) return;
    update(state => ({
      ...state, isWaitingForResponse: false,
      error: error instanceof Error ? error.message : 'Unable to reach Mr. Bloom.',
      chatHistory: state.chatHistory.map(msg => msg.id === msgId ? { ...msg, status: 'failed' } : msg)
    }));
  }
}

function createMrBloomStore() {
  const now = new Date();
  const vietnamese = typeof navigator !== 'undefined' && navigator.language.toLowerCase().startsWith('vi');
  const greeting = vietnamese
    ? now.getHours() < 12 ? 'Chào buổi sáng' : now.getHours() < 18 ? 'Chào buổi chiều' : 'Chào buổi tối'
    : now.getHours() < 12 ? 'Good morning' : now.getHours() < 18 ? 'Good afternoon' : 'Good evening';
  const greetingBody = vietnamese ? 'Hôm nay bạn muốn làm việc gì?' : 'What would you like to work on today?';
  const initial: MrBloomState = {
    chatHistory: [{ id: '1', role: 'assistant', content: `${greeting}.\n${greetingBody}`, timestamp: timeLabel() }],
    isWaitingForResponse: false, activeDraft: null, preview: null,
    previewMode: 'placeholder', sessionId: null, degraded: null,
    suggestions: [], assumptions: [], needsReplace: false, error: null
  };
  const { subscribe, set, update } = writable<MrBloomState>(initial);

  async function submit(content: string, retryId?: string) {
    const message = content.trim();
    if (!message) return;
    let accepted = false;
    let snapshot = initial;
    const msgId = retryId ?? crypto.randomUUID();
    update(state => {
      if (state.isWaitingForResponse) return state;
      accepted = true;
      snapshot = state;
      return {
        ...state, error: null, isWaitingForResponse: true,
        chatHistory: retryId
          ? state.chatHistory.map(item => item.id === retryId ? { ...item, status: undefined } : item)
          : [...state.chatHistory, { id: msgId, role: 'user', content: message, timestamp: timeLabel() }]
      };
    });
    if (accepted) await sendMessage(message, msgId, update, snapshot);
  }

  async function doApplyPatch(ops: Record<string, unknown>[]) {
    let draft: AssistantDraft | null = null;
    update(state => { draft = state.activeDraft; return { ...state, error: null }; });
    if (!draft) return;
    try {
      const result = await api.post('/assistant/apply-patch', { draft, ops });
      update(state => ({
        ...state,
        activeDraft: result.draft,
        preview: result.preview ?? null,
        previewMode: result.preview ? 'timeline' : result.draft.type,
        needsReplace: false
      }));
    } catch (error) {
      update(state => ({ ...state, error: error instanceof Error ? error.message : 'Edit failed.' }));
    }
  }
  let patchQueue: Promise<void> = Promise.resolve();
  function applyPatch(ops: Record<string, unknown>[]): Promise<void> {
    const next = patchQueue.then(() => doApplyPatch(ops));
    patchQueue = next;
    return next;
  }

  const pendingDuration = new Map<string, number>();
  let previewTimer: ReturnType<typeof setTimeout> | undefined;
  async function flushPendingDurations() {
    if (previewTimer) clearTimeout(previewTimer);
    previewTimer = undefined;
    if (!pendingDuration.size) return;
    const ops = [...pendingDuration].map(([task_id, duration_min]) =>
      ({ op: 'update_task', task_id, duration_min }));
    pendingDuration.clear();
    await applyPatch(ops);
  }
  function scheduleDuration(taskId: string, durationMin: number) {
    pendingDuration.set(taskId, durationMin);
    if (previewTimer) clearTimeout(previewTimer);
    previewTimer = setTimeout(() => { void flushPendingDurations(); }, 300);
  }

  async function saveToday(replaceExisting = false) {
    await flushPendingDurations();
    await patchQueue;
    ++latestRequestVersion; let snapshot: MrBloomState = initial;
    update(state => { snapshot = state; return { ...state, error: null }; });
    if (snapshot.error) return;
    if (snapshot.activeDraft?.type !== 'today' || !snapshot.preview) return;
    const performSave = async (preview: TodayPreviewResponse) =>
      saveTodayPlan(snapshot.sessionId, preview.preview_token, snapshot.activeDraft as TodayDraft, replaceExisting);
    try {
      await performSave(snapshot.preview);
      update(state => ({
        ...state, activeDraft: null, preview: null, previewMode: 'placeholder', needsReplace: false,
        suggestions: [], assumptions: [],
        chatHistory: [...state.chatHistory, { id: crypto.randomUUID(), role: 'assistant', content: 'Your schedule was saved to Today.', timestamp: timeLabel() }]
      }));
    } catch (error) {
      if (error instanceof APIError && error.status === 409 && error.detail?.detail?.code === 'PLAN_EXISTS') {
        const message = error.message;
        update(state => ({ ...state, needsReplace: true, error: message }));
        return;
      }
      if (error instanceof APIError && error.status === 409) {
        try {
          const refreshed = await previewTodayPlan(snapshot.activeDraft);
          await performSave(refreshed);
          update(state => ({ ...state, activeDraft: null, preview: null, previewMode: 'placeholder', needsReplace: false, suggestions: [], assumptions: [] }));
          return;
        } catch (retryError) { error = retryError; }
      }
      update(state => ({ ...state, error: error instanceof Error ? error.message : 'Save failed.' }));
    }
  }

  async function persistRoadmap() {
    ++latestRequestVersion; let snapshot = initial;
    update(state => { snapshot = state; return { ...state, error: null }; });
    if (snapshot.activeDraft?.type !== 'roadmap') return false;
    try {
      await saveRoadmap(snapshot.sessionId, snapshot.activeDraft);
      update(state => ({
        ...state,
        activeDraft: null,
        preview: null,
        previewMode: 'placeholder',
        suggestions: [],
        assumptions: [],
        chatHistory: [...state.chatHistory, { id: crypto.randomUUID(), role: 'assistant', content: 'Your roadmap was saved to Goals.', timestamp: timeLabel() }]
      }));
      return true;
    } catch (error) {
      update(state => ({ ...state, error: error instanceof Error ? error.message : 'Failed to save goal.' }));
      return false;
    }
  }

  const store = {
    subscribe, set, update,
    submitMessage: (content: string) => submit(content),
    retryMessage: async (id: string) => {
      let content = '';
      update(state => { content = state.chatHistory.find(item => item.id === id && item.status === 'failed')?.content ?? ''; return state; });
      if (content) await submit(content, id);
    },
    restoreLatestSession: async () => {
      let shouldRestore = false;
      update(state => {
        shouldRestore = state.sessionId === null && state.activeDraft === null && state.chatHistory.length <= 1;
        return state;
      });
      if (!shouldRestore) return;
      
      const version = ++latestRequestVersion;
      try {
        const session = await api.get('/assistant/sessions/latest') as AssistantSession;
        if (version !== latestRequestVersion) return;
        
        const latestPayload = [...session.messages]
          .reverse()
          .find(message => message.role === 'assistant' && message.structured_payload)
          ?.structured_payload;
        const draft = (latestPayload?.draft ?? null) as AssistantDraft | null;
        update(state => ({
          ...state,
          sessionId: session.session_id,
          chatHistory: session.messages.map(message => ({
            id: crypto.randomUUID(),
            role: message.role,
            content: message.content,
            timestamp: new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          })),
          activeDraft: draft,
          preview: (latestPayload?.preview ?? null) as TodayPreviewResponse | null,
          previewMode: draft?.type ?? 'placeholder',
          degraded: (latestPayload?.degraded ?? null) as string | null,
          suggestions: (latestPayload?.suggestions ?? []) as AssistantSuggestion[],
          assumptions: (latestPayload?.assumptions ?? []) as AssistantAssumption[],
          error: null
        }));
      } catch (error) {
        if (version !== latestRequestVersion) return;
        if (!(error instanceof APIError && error.status === 404)) {
          update(state => ({ ...state, error: error instanceof Error ? error.message : 'Session reload failed.' }));
        }
      }
    },
    discardDraft: () => {
      ++latestRequestVersion;
      update(state => ({ ...state, activeDraft: null, preview: null, previewMode: 'placeholder', suggestions: [], assumptions: [], needsReplace: false }));
    },
    acceptDraft: (message: string) => {
      ++latestRequestVersion;
      update(state => ({
        ...state, activeDraft: null, preview: null, previewMode: 'placeholder', suggestions: [], assumptions: [], needsReplace: false,
        chatHistory: [...state.chatHistory, { id: crypto.randomUUID(), role: 'assistant', content: message, timestamp: timeLabel() }]
      }));
    },
    applyPatch,
    updateTaskDuration: scheduleDuration,
    addTask: (title: string, durationMin: number) => {
      const clean = title.trim();
      if (!clean || !Number.isFinite(durationMin) || durationMin < 5 || durationMin > 480) return;
      const task: TaskDraft = {
        id: crypto.randomUUID(), title: clean, durationMin,
        priority: 'MEDIUM', importance: 'CORE', category: 'Personal',
        estimateSource: 'USER', breakAfterMin: 5, deadline: null,
        schedulingType: 'FLEXIBLE', fixedStart: null, fixedEnd: null,
        dependencies: [], splittable: false
      };
      return flushPendingDurations().then(() => applyPatch([{ op: 'add_task', task }]));
    },
    updateTaskImportance: (taskId: string, importance: Importance) =>
      flushPendingDurations().then(() => applyPatch([{ op: 'update_task', task_id: taskId, importance }])),
    removeTask: (taskId: string) =>
      flushPendingDurations().then(() => applyPatch([{ op: 'remove_task', task_id: taskId }])),
    generateTimeline: async () => {
      await flushPendingDurations();
      await patchQueue;
      let draft: TodayDraft | null = null;
      let patchError = false;
      update(state => { draft = state.activeDraft?.type === 'today' ? state.activeDraft : null; patchError = !!state.error; return { ...state, error: patchError ? state.error : null }; });
      if (patchError) return;
      if (!draft) return;
      try {
        const preview = await previewTodayPlan(draft);
        update(state => ({ ...state, preview, previewMode: 'timeline' }));
      } catch (error) {
        update(state => ({ ...state, error: error instanceof Error ? error.message : 'Preview failed.' }));
      }
    },
    saveToday,
    receiveNudge: (nudge: { message: string; action: string }) => update(state => ({
      ...state,
      chatHistory: [...state.chatHistory, { id: crypto.randomUUID(), role: 'assistant', content: nudge.message, timestamp: timeLabel() }],
      suggestions: nudge.action === 'PLAN_TODAY'
        ? [{ label: 'Make a plan', send_text: 'Plan my day' }]
        : nudge.action === 'REPLAN_TODAY'
          ? [{ label: 'Replan today', action: 'REPLAN_TODAY' }]
          : state.suggestions
    })),
    saveRoadmap: persistRoadmap,
    handleSuggestion: async (suggestion: AssistantSuggestion) => {
      if (suggestion.patch?.length) return applyPatch(suggestion.patch);
      if (suggestion.send_text) return submit(suggestion.send_text);
      if (suggestion.action === 'SAVE_TODAY') return saveToday();
      if (suggestion.action === 'SAVE_ROADMAP') return persistRoadmap();
      if (suggestion.action === 'SKIP_OPTIONAL_TODAY') {
        try {
          await api.post('/assistant/actions/SKIP_OPTIONAL_TODAY', {});
          update(state => ({
            ...state,
            suggestions: [],
            chatHistory: [...state.chatHistory, { id: crypto.randomUUID(), role: 'assistant', content: 'Optional tasks were skipped and today was replanned.', timestamp: timeLabel() }]
          }));
        } catch (error) {
          update(state => ({ ...state, error: error instanceof Error ? error.message : 'Action failed.' }));
        }
        return;
      }
      if (suggestion.action === 'REPLAN_TODAY') {
        try { await api.post('/assistant/actions/REPLAN_TODAY', {}); }
        catch (error) { update(state => ({ ...state, error: error instanceof Error ? error.message : 'Action failed.' })); }
        return;
      }
      return submit(suggestion.label);
    },
    backToTasks: () => update(state => ({ ...state, previewMode: 'today' }))
  };
  return store;
}

export const mrBloomStore = createMrBloomStore();
