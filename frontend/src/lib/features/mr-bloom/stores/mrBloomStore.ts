import { writable } from 'svelte/store';
import {
  api, APIError, previewTodayPlan, saveTodayPlan,
  type TodayDraft, type RoadmapDraft, type TaskDraft, type MilestoneDraft,
  type AssistantDraft, type TodayPreviewResponse, type AssistantSuggestion,
  type AssistantAssumption, type AssistantSession, saveRoadmap, type ChatResponse
} from '$lib/api';
import type { IconName } from '$lib/shared/components/atoms/AppIcon.svelte';
import { goto } from '$app/navigation';

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
  isDraftMutationPending?: boolean;
  isPreviewPending?: boolean;
  isSavePending?: boolean;
  error?: string | null;
}

function timeLabel() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function apiErrorCode(error: APIError): string | null {
  if (!error.detail || typeof error.detail !== 'object' || !('detail' in error.detail)) return null;
  const detail = error.detail.detail;
  return detail && typeof detail === 'object' && 'code' in detail && typeof detail.code === 'string'
    ? detail.code
    : null;
}

let latestRequestVersion = 0;

// A discard, save or session restore invalidates an in-flight reply. The reply
// is dropped, but the composer must still be released: only one chat request
// can be in flight, so no newer request depends on this flag staying set.
function releaseComposer(update: (updater: (state: MrBloomState) => MrBloomState) => void) {
  update(state => (state.isWaitingForResponse ? { ...state, isWaitingForResponse: false } : state));
}

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
    if (version !== latestRequestVersion) return releaseComposer(update);
    update(state => ({
      ...state, isWaitingForResponse: false,
      activeDraft: result.draft ?? state.activeDraft,
      // A draft-edit response may include a scheduler-issued fresh preview.
      // A newly generated draft has no preview and must still be reviewed.
      preview: result.draft
        ? (result.intent === 'EDIT_DRAFT' ? (result.preview ?? null) : null)
        : (result.preview ?? state.preview),
      previewMode: result.intent === 'EDIT_DRAFT' && result.preview
        ? 'timeline'
        : (result.draft?.type ?? state.previewMode),
      sessionId: result.session_id ?? state.sessionId,
      degraded: result.degraded ?? null,
      suggestions: result.suggestions ?? [],
      assumptions: result.assumptions ?? [],
      chatHistory: [...state.chatHistory, {
        id: crypto.randomUUID(), role: 'assistant', content: result.reply, timestamp: timeLabel()
      }]
    }));
  } catch (error) {
    if (version !== latestRequestVersion) return releaseComposer(update);
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
    suggestions: [], assumptions: [], needsReplace: false,
    isDraftMutationPending: false, isPreviewPending: false, isSavePending: false, error: null
  };
  const { subscribe, set, update } = writable<MrBloomState>(initial);
  let draftRevision = 0;
  let previewSequence = 0;
  let roadmapSaveKey: string | null = null;

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

  function clockOnPlanDate(planDate: string, value: string | null | undefined) {
    return value ? `${planDate}T${value}:00` : null;
  }

  function applyLocalTodayOps(draft: TodayDraft, ops: import('$lib/api').PatchOp[]): TodayDraft {
    let next = draft;
    for (const op of ops) {
      if (op.op === 'set_windows') {
        next = { ...next, windows: op.windows.map(window => ({ ...window })) };
      } else if (op.op === 'update_window') {
        next = { ...next, windows: next.windows.map((window, index) => index === op.window_index
          ? { start: op.start ?? window.start, end: op.end ?? window.end }
          : window) };
      } else if (op.op === 'add_task') {
        next = { ...next, tasks: [...next.tasks, { ...op.task }] };
      } else if (op.op === 'remove_task') {
        next = { ...next, tasks: next.tasks.filter(task => task.id !== op.task_id) };
      } else if (op.op === 'remove_deferred_task') {
        next = { ...next, deferred_tasks: (next.deferred_tasks ?? []).filter(item => item.task.id !== op.task_id) };
      } else if (op.op === 'scale_durations') {
        next = { ...next, tasks: next.tasks.map(task => !op.task_id || task.id === op.task_id
          ? { ...task, durationMin: Math.min(480, Math.max(5, Math.round(task.durationMin * op.factor / 5) * 5)), estimateSource: 'USER' }
          : task) };
      } else if (op.op === 'set_plan_date') {
        next = { ...next, planDate: op.plan_date };
      } else if (op.op === 'update_task') {
        next = { ...next, tasks: next.tasks.map(task => task.id !== op.task_id ? task : {
          ...task,
          ...(op.title !== undefined && op.title !== null ? { title: op.title } : {}),
          ...(op.duration_min !== undefined && op.duration_min !== null
            ? { durationMin: op.duration_min, estimateSource: 'USER' as const } : {}),
          ...(op.importance !== undefined && op.importance !== null ? { importance: op.importance } : {}),
          ...(op.priority !== undefined && op.priority !== null ? { priority: op.priority === 'URGENT' ? 'HIGH' as const : op.priority } : {}),
          ...(op.category !== undefined ? { category: op.category } : {}),
          ...(op.break_after_min !== undefined ? { breakAfterMin: op.break_after_min } : {}),
          ...(op.splittable !== undefined && op.splittable !== null ? { splittable: op.splittable } : {}),
          ...(op.scheduling_type !== undefined && op.scheduling_type !== null ? { schedulingType: op.scheduling_type } : {}),
          ...(op.fixed_start !== undefined ? { fixedStart: clockOnPlanDate(next.planDate, op.fixed_start) } : {}),
          ...(op.fixed_end !== undefined ? { fixedEnd: clockOnPlanDate(next.planDate, op.fixed_end) } : {}),
          ...(op.deadline !== undefined ? { deadline: clockOnPlanDate(next.planDate, op.deadline) } : {})
        }) };
      }
    }
    return next;
  }
  function applyPatch(ops: import('$lib/api').PatchOp[]): Promise<void> {
    draftRevision += 1;
    previewSequence += 1;
    update(state => {
      if (state.activeDraft?.type !== 'today') return state;
      const activeDraft = applyLocalTodayOps(state.activeDraft, ops);
      return {
        ...state, activeDraft, preview: null, previewMode: 'today',
        needsReplace: false, isDraftMutationPending: false,
        isPreviewPending: false, error: null
      };
    });
    return Promise.resolve();
  }

  function scheduleDuration(taskId: string, durationMin: number) {
    void applyPatch([{ op: 'update_task', task_id: taskId, duration_min: durationMin }]);
  }
  function scheduleTitle(taskId: string, title: string) {
    void applyPatch([{ op: 'update_task', task_id: taskId, title }]);
  }

  async function saveToday(replaceExisting = false) {
    let accepted = false;
    update(state => {
      if (state.isSavePending) return state;
      accepted = true;
      return { ...state, error: null, isSavePending: true };
    });
    if (!accepted) return;
    ++latestRequestVersion;
    try {
      let snapshot = initial;
      update(state => { snapshot = state; return state; });
      if (snapshot.activeDraft?.type !== 'today' || !snapshot.preview) return;
      await saveTodayPlan(
        snapshot.sessionId, snapshot.preview.preview_token, snapshot.activeDraft, replaceExisting
      );
      update(state => ({
        ...state, activeDraft: null, preview: null, previewMode: 'placeholder', sessionId: null,
        needsReplace: false, isSavePending: false,
        suggestions: [], assumptions: [],
        chatHistory: [...state.chatHistory, { id: crypto.randomUUID(), role: 'assistant', content: 'Your schedule was saved to Today.', timestamp: timeLabel() }]
      }));
      void Promise.resolve(
        goto(`/today?date=${encodeURIComponent(snapshot.activeDraft.planDate)}`)
      ).catch(() => {
        // The save is already committed; a navigation failure must not turn it
        // into a failed/retried replacement.
      });
    } catch (error) {
      if (error instanceof APIError && error.status === 409 && apiErrorCode(error) === 'PLAN_EXISTS') {
        update(state => ({ ...state, needsReplace: true, error: null }));
        return;
      }
      if (error instanceof APIError && error.status === 409 && apiErrorCode(error) === 'PREVIEW_STALE') {
        // Never turn a stale/conflicting preview into an implicit save.  Keep
        // every user edit, invalidate the capability, and require the user to
        // review a fresh scheduler result.
        update(state => ({
          ...state,
          preview: null,
          previewMode: state.activeDraft?.type ?? 'placeholder',
          needsReplace: false,
          error: error instanceof Error ? error.message : 'Preview is stale. Generate it again before saving.'
        }));
        return;
      }
      update(state => ({ ...state, error: error instanceof Error ? error.message : 'Save failed.' }));
    } finally {
      update(state => ({ ...state, isSavePending: false }));
    }
  }

  async function persistRoadmap() {
    ++latestRequestVersion; let snapshot = initial; let accepted = false;
    update(state => {
      snapshot = state;
      if (state.isSavePending) return state;
      accepted = true;
      return { ...state, error: null, isSavePending: true };
    });
    if (!accepted) return false;
    if (snapshot.activeDraft?.type !== 'roadmap') {
      update(state => ({ ...state, isSavePending: false }));
      return false;
    }
    try {
      roadmapSaveKey ??= crypto.randomUUID();
      await saveRoadmap(snapshot.sessionId, snapshot.activeDraft, roadmapSaveKey);
      update(state => ({
        ...state,
        activeDraft: null,
        preview: null,
        previewMode: 'placeholder',
        suggestions: [],
        assumptions: [],
        isSavePending: false,
        chatHistory: [...state.chatHistory, { id: crypto.randomUUID(), role: 'assistant', content: 'Your roadmap was saved to Goals.', timestamp: timeLabel() }]
      }));
      roadmapSaveKey = null;
      return true;
    } catch (error) {
      update(state => ({ ...state, isSavePending: false, error: error instanceof Error ? error.message : 'Failed to save goal.' }));
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
          // The sessions endpoint removes expired/stale capabilities before
          // returning structured payloads, so a remaining preview is trusted.
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
    updateRoadmap: (changes: Partial<Pick<RoadmapDraft, 'goalTitle' | 'goalDescription' | 'targetDate'>>) =>
      update(state => state.activeDraft?.type === 'roadmap'
        ? { ...state, activeDraft: { ...state.activeDraft, ...changes }, error: null }
        : state),
    updateMilestone: (milestoneId: string, changes: Partial<MilestoneDraft>) =>
      update(state => state.activeDraft?.type === 'roadmap'
        ? {
            ...state,
            activeDraft: {
              ...state.activeDraft,
              milestones: state.activeDraft.milestones.map(item =>
                item.id === milestoneId ? { ...item, ...changes, id: item.id } : item
              )
            },
            error: null
          }
        : state),
    removeMilestone: (milestoneId: string) =>
      update(state => state.activeDraft?.type === 'roadmap'
        ? { ...state, activeDraft: { ...state.activeDraft, milestones: state.activeDraft.milestones.filter(item => item.id !== milestoneId) } }
        : state),
    addMilestone: () => update(state => {
      if (state.activeDraft?.type !== 'roadmap' || state.activeDraft.milestones.length >= 12) return state;
      return {
        ...state,
        activeDraft: {
          ...state.activeDraft,
          milestones: [...state.activeDraft.milestones, {
            id: (() => {
              const used = new Set(state.activeDraft.milestones.map(item => item.id));
              let number = 1;
              while (used.has(`m${number}`)) number += 1;
              return `m${number}`;
            })(), title: 'New milestone',
            targetDate: state.activeDraft.targetDate, expectedOutcome: null
          }]
        }
      };
    }),
    updateTaskDuration: scheduleDuration,
    updateTaskTitle: scheduleTitle,
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
      return applyPatch([{ op: 'add_task' as const, task }]);
    },
    updateTaskImportance: (taskId: string, importance: Importance) =>
      applyPatch([{ op: 'update_task' as const, task_id: taskId, importance: importance as 'CORE' | 'OPTIONAL' }]),
    removeTask: (taskId: string) =>
      applyPatch([{ op: 'remove_task' as const, task_id: taskId }]),
    removeDeferredTask: (taskId: string) =>
      applyPatch([{ op: 'remove_deferred_task' as const, task_id: taskId }]),
    generateTimeline: async () => {
      let draft: TodayDraft | null = null;
      let patchError = false;
      update(state => { draft = state.activeDraft?.type === 'today' ? state.activeDraft : null; patchError = !!state.error; return { ...state, error: patchError ? state.error : null }; });
      if (patchError) return;
      if (!draft) return;
      const revision = draftRevision;
      const requestSequence = ++previewSequence;
      update(state => ({ ...state, preview: null, previewMode: state.activeDraft?.type ?? 'placeholder', isPreviewPending: true }));
      try {
        const preview = await previewTodayPlan(draft);
        update(state => {
          if (requestSequence !== previewSequence) return state;
          if (revision !== draftRevision) return { ...state, isPreviewPending: false };
          return { ...state, preview, previewMode: 'timeline', isPreviewPending: false };
        });
      } catch (error) {
        update(state => {
          if (requestSequence !== previewSequence) return state;
          if (revision !== draftRevision) return { ...state, isPreviewPending: false };
          return { ...state, isPreviewPending: false, error: error instanceof Error ? error.message : 'Preview failed.' };
        });
      }
    },
    saveToday,
    cancelReplace: () => update(state => ({ ...state, needsReplace: false, error: null })),
    confirmReplace: () => saveToday(true),
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
      if (suggestion.action) {
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
        return;
      }
      return submit(suggestion.label);
    },
    backToTasks: () => update(state => ({ ...state, previewMode: 'today' }))
  };
  return store;
}

export const mrBloomStore = createMrBloomStore();
