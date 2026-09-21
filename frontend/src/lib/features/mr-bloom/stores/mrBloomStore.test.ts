import { beforeEach, expect, test, vi } from 'vitest';
import { get } from 'svelte/store';
import { api, type TodayDraft } from '$lib/api';
import { mrBloomStore } from './mrBloomStore';

vi.mock('$lib/api', () => ({
  api: { post: vi.fn(), get: vi.fn() },
  previewTodayPlan: vi.fn(),
  saveTodayPlan: vi.fn(),
  saveRoadmap: vi.fn()
}));

beforeEach(() => {
  vi.clearAllMocks();
  mrBloomStore.set({ chatHistory: [], isWaitingForResponse: false, activeDraft: null, preview: null, previewMode: 'placeholder', sessionId: null, degraded: null, suggestions: [], assumptions: [], needsReplace: false, error: null });
});

test('sends the message to the backend and shows its draft', async () => {
  vi.mocked(api.post).mockResolvedValue({
    reply: 'Review these tasks.',
    draft: { type: 'today', planDate: '2026-09-20', timezone: 'UTC', windows: [{ start: '09:00', end: '12:00' }], tasks: [
      { id: 'task-1', title: 'Write report', durationMin: 90, priority: 'MEDIUM', importance: 'CORE',
        category: null, estimateSource: 'USER', breakAfterMin: null, deadline: null,
        schedulingType: 'FLEXIBLE', fixedStart: null, fixedEnd: null, dependencies: [], splittable: false }
    ] }
  });

  await mrBloomStore.submitMessage('Plan my report');

  expect(api.post).toHaveBeenCalledWith('/assistant/chat', { message: 'Plan my report', session_id: null, current_draft: null });
  const state = get(mrBloomStore);
  expect(state.chatHistory.at(-1)?.content).toBe('Review these tasks.');
  expect(state.activeDraft?.type).toBe('today');
  if (state.activeDraft?.type === 'today') {
    expect(state.activeDraft.tasks[0].id).toBe('task-1');
    expect(state.activeDraft.tasks[0].title).toBe('Write report');
    vi.mocked(api.post).mockResolvedValueOnce({
      draft: { ...state.activeDraft, tasks: state.activeDraft.tasks.map(task => ({ ...task, importance: 'OPTIONAL' })) },
      preview: { preview_token: 'fresh' }
    });
    await mrBloomStore.updateTaskImportance('task-1', 'OPTIONAL');
    const edited = get(mrBloomStore).activeDraft;
    if (edited?.type === 'today') {
      expect(edited.tasks[0].importance).toBe('OPTIONAL');
      expect(edited.tasks[0].priority).toBe('MEDIUM');
    }
  }
  expect(state.isWaitingForResponse).toBe(false);
});

test('shows a service error and keeps the composer available', async () => {
  vi.mocked(api.post).mockRejectedValue(new Error('Service unavailable'));
  await mrBloomStore.submitMessage('Help me plan');
  const state = get(mrBloomStore);
  expect(state.error).toBe('Service unavailable');
  expect(state.isWaitingForResponse).toBe(false);
  expect(state.activeDraft).toBeNull();
});

test('failed message is marked as failed and excluded from outgoing history on retry', async () => {
  // 1. Initial success
  vi.mocked(api.post).mockResolvedValueOnce({
    reply: 'First reply', draft: null
  });
  await mrBloomStore.submitMessage('First message');

  // 2. Failure
  vi.mocked(api.post).mockRejectedValueOnce(new Error('Network error'));
  await mrBloomStore.submitMessage('Failing message');

  let state = get(mrBloomStore);
  expect(state.error).toBe('Network error');
  const failedMsg = state.chatHistory.at(-1)!;
  expect(failedMsg.content).toBe('Failing message');
  expect(failedMsg.status).toBe('failed');

  // 3. Retry success
  vi.mocked(api.post).mockResolvedValueOnce({
    reply: 'Recovered reply', draft: null
  });
  await mrBloomStore.retryMessage(failedMsg.id);

  state = get(mrBloomStore);
  expect(state.error).toBeNull();
  
  expect(api.post).toHaveBeenLastCalledWith('/assistant/chat', expect.objectContaining({ message: 'Failing message' }));

  const userMessages = state.chatHistory.filter(m => m.role === 'user');
  expect(userMessages.length).toBe(2);
  expect(userMessages[1].status).toBeUndefined(); // Status cleared
});

test('restores the latest server-owned session including draft metadata', async () => {
  vi.mocked(api.get).mockResolvedValue({
    session_id: 'session-1',
    status: 'OPEN',
    messages: [
      { role: 'user', content: 'Plan study', created_at: '2026-09-20T08:00:00Z', structured_payload: null },
      {
        role: 'assistant', content: 'Review it', created_at: '2026-09-20T08:00:01Z',
        structured_payload: {
          draft: { type: 'today', planDate: '2026-09-20', timezone: 'UTC', windows: [], tasks: [] },
          suggestions: [{ label: 'Save plan', action: 'SAVE_TODAY' }],
          assumptions: [{ id: 'a1', kind: 'WINDOW', text: 'Assumed 09:00-17:00', task_id: null }],
          degraded: 'LEAN'
        }
      }
    ]
  });
  await mrBloomStore.restoreLatestSession();
  const state = get(mrBloomStore);
  expect(state.sessionId).toBe('session-1');
  expect(state.chatHistory).toHaveLength(2);
  expect(state.activeDraft?.type).toBe('today');
  expect(state.suggestions[0].action).toBe('SAVE_TODAY');
  expect(state.assumptions[0].id).toBe('a1');
  expect(state.degraded).toBe('LEAN');
});

test('executes an allowlisted quick reply action explicitly', async () => {
  vi.mocked(api.post).mockResolvedValue({ status: 'ACTIVE', blocks: [] });
  const suggestion = { label: 'Skip optional tasks', action: 'SKIP_OPTIONAL_TODAY' };
  mrBloomStore.update(state => ({ ...state, suggestions: [suggestion] }));
  await mrBloomStore.handleSuggestion(suggestion);
  expect(api.post).toHaveBeenCalledWith('/assistant/actions/SKIP_OPTIONAL_TODAY', {});
  expect(get(mrBloomStore).suggestions).toEqual([]);
});

test('send-text and patch quick replies use their explicit payloads', async () => {
  vi.mocked(api.post).mockResolvedValueOnce({ reply: 'Ready', draft: null });
  await mrBloomStore.handleSuggestion({ label: 'Plan', send_text: 'Plan my day' });
  expect(api.post).toHaveBeenCalledWith('/assistant/chat', expect.objectContaining({ message: 'Plan my day' }));

  const draft: TodayDraft = { type: 'today', planDate: '2026-09-20', timezone: 'UTC',
    windows: [{ start: '09:00', end: '12:00' }], tasks: [] };
  mrBloomStore.update(state => ({ ...state, activeDraft: draft }));
  vi.mocked(api.post).mockResolvedValueOnce({ draft, preview: null });
  const patch = [{ op: 'set_windows', windows: [{ start: '10:00', end: '12:00' }] }];
  await mrBloomStore.handleSuggestion({ label: 'Start later', patch });
  expect(api.post).toHaveBeenLastCalledWith('/assistant/apply-patch', { draft, ops: patch });
});

test('duration edits debounce into one preview request', async () => {
  vi.useFakeTimers();
  try {
    const draft: TodayDraft = { type: 'today', planDate: '2026-09-20', timezone: 'UTC',
      windows: [{ start: '09:00', end: '12:00' }], tasks: [{ id: 'd1', title: 'Read',
        durationMin: 30, priority: 'MEDIUM', importance: 'CORE', category: null,
        estimateSource: 'USER', breakAfterMin: null, deadline: null,
        schedulingType: 'FLEXIBLE', fixedStart: null, fixedEnd: null,
        dependencies: [], splittable: false }] };
    mrBloomStore.update(state => ({ ...state, activeDraft: draft }));
    vi.mocked(api.post).mockResolvedValue({ draft, preview: null });
    mrBloomStore.updateTaskDuration('d1', 35);
    mrBloomStore.updateTaskDuration('d1', 40);
    await vi.advanceTimersByTimeAsync(300);
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(api.post).toHaveBeenCalledWith('/assistant/apply-patch', {
      draft, ops: [{ op: 'update_task', task_id: 'd1', duration_min: 40 }]
    });
  } finally {
    vi.useRealTimers();
  }
});

test('SS-011, PR-016: Stale response protection prevents older requests from overwriting newer state', async () => {
  let resolveA: (val: any) => void;
  const promiseA = new Promise((resolve) => { resolveA = resolve; });
  vi.mocked(api.post).mockReturnValueOnce(promiseA);

  // Set an initial active draft so discardDraft makes semantic sense
  mrBloomStore.update(s => ({ ...s, activeDraft: { type: 'today', planDate: '2026-01-01', tasks: [] } as any }));

  // Request A starts through submitMessage()
  const pending = mrBloomStore.submitMessage('Change something');

  // A legitimate public store action changes/invalidates the authoritative context
  mrBloomStore.discardDraft();

  let state = get(mrBloomStore);
  expect(state.activeDraft).toBeNull();

  // A resolves late
  resolveA!({
    reply: 'Late reply',
    session_id: 'stale-session',
    draft: { type: 'today', planDate: '2026-01-02', tasks: [] }
  });
  await pending;

  // A must NOT restore stale session/draft state
  state = get(mrBloomStore);
  expect(state.sessionId).not.toBe('stale-session');
  expect(state.activeDraft).toBeNull();
});
