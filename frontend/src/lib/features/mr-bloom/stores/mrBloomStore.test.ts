import { beforeEach, expect, test, vi } from 'vitest';
import { get } from 'svelte/store';
import { api, saveTodayPlan, type TodayDraft } from '$lib/api';
import { mrBloomStore } from './mrBloomStore';
import { goto } from '$app/navigation';

vi.mock('$app/navigation', () => ({ goto: vi.fn() }));

vi.mock('$lib/api', () => ({
  APIError: class APIError extends Error {
    constructor(public status: number, public detail: unknown) { super('API error'); }
  },
  api: { post: vi.fn(), get: vi.fn() },
  previewTodayPlan: vi.fn(),
  saveTodayPlan: vi.fn(),
  saveRoadmap: vi.fn()
}));

const saveableDraft: TodayDraft = {
  type: 'today', planDate: '2026-09-20', timezone: 'UTC', windows: [], tasks: []
};

beforeEach(() => {
  vi.clearAllMocks();
  mrBloomStore.set({ chatHistory: [], isWaitingForResponse: false, activeDraft: null, preview: null, previewMode: 'placeholder', sessionId: null, degraded: null, suggestions: [], assumptions: [], needsReplace: false, selectedTaskId: null, error: null });
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

test('chat edit sends the complete current task fields and invalidates old preview', async () => {
  const draft: TodayDraft = {
    type: 'today', planDate: '2026-09-20', timezone: 'UTC', windows: [],
    tasks: [{
      id: 'd2', title: 'Read Book', durationMin: 30, priority: 'MEDIUM', importance: 'CORE',
      category: null, estimateSource: 'USER', breakAfterMin: null, deadline: null,
      schedulingType: 'FLEXIBLE', fixedStart: null, fixedEnd: null, dependencies: [], splittable: false
    }]
  };
  const edited = {
    ...draft, tasks: [{ ...draft.tasks[0], durationMin: 20, importance: 'OPTIONAL' as const }]
  };
  mrBloomStore.update(state => ({
    ...state, activeDraft: draft, preview: { preview_token: 'old' } as never,
    previewMode: 'timeline', sessionId: 'session-1'
  }));
  vi.mocked(api.post).mockResolvedValueOnce({
    reply: 'Updated', intent: 'EDIT_DRAFT', draft: edited, preview: null
  });

  await mrBloomStore.submitMessage('Change Read a book to 20 minutes and mark it optional.');

  expect(api.post).toHaveBeenCalledWith('/assistant/chat', {
    message: 'Change Read a book to 20 minutes and mark it optional.',
    session_id: 'session-1',
    current_draft: draft
  });
  const state = get(mrBloomStore);
  expect(state.activeDraft).toEqual(edited);
  expect(state.preview).toBeNull();
  expect(state.previewMode).toBe('today');
});

test('CHAT-04: conversational reply preserves an existing draft and message order', async () => {
  mrBloomStore.update(state => ({ ...state, activeDraft: saveableDraft }));
  vi.mocked(api.post).mockResolvedValueOnce({
    reply: 'Glad to help. Ready to keep going?', intent: 'THANKS', draft: null
  });

  await mrBloomStore.submitMessage('Thanks');

  const state = get(mrBloomStore);
  expect(state.activeDraft).toEqual(saveableDraft);
  expect(state.chatHistory.map(message => [message.role, message.content])).toEqual([
    ['user', 'Thanks'],
    ['assistant', 'Glad to help. Ready to keep going?']
  ]);
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
  const patch: import('$lib/api').PatchOp[] = [{ op: 'set_windows' as const, windows: [{ start: '10:00', end: '12:00' }] }];
  await mrBloomStore.handleSuggestion({ label: 'Start later', patch });
  expect(get(mrBloomStore).activeDraft).toEqual({ ...draft, windows: [{ start: '10:00', end: '12:00' }] });
  expect(api.post).toHaveBeenCalledTimes(1);
});

test('duration edits stay local and do not automatically preview', () => {
  const draft: TodayDraft = { type: 'today', planDate: '2026-09-20', timezone: 'UTC',
    windows: [{ start: '09:00', end: '12:00' }], tasks: [{ id: 'd1', title: 'Read',
      durationMin: 30, priority: 'MEDIUM', importance: 'CORE', category: null,
      estimateSource: 'USER', breakAfterMin: null, deadline: null,
      schedulingType: 'FLEXIBLE', fixedStart: null, fixedEnd: null,
      dependencies: [], splittable: false }] };
  mrBloomStore.update(state => ({ ...state, activeDraft: draft }));
  mrBloomStore.updateTaskDuration('d1', 35);
  mrBloomStore.updateTaskDuration('d1', 40);
  const edited = get(mrBloomStore).activeDraft;
  expect(edited?.type === 'today' && edited.tasks[0].durationMin).toBe(40);
  expect(api.post).not.toHaveBeenCalled();
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


test('MD-008: safely ignores unsupported actions', async () => {
  const initialState = get(mrBloomStore);
  
  vi.mocked(api.post).mockClear();
  const suggestion = { label: 'Delete account', action: 'delete_account' };
  
  // Provide the suggestion so it can be handled
  mrBloomStore.update(state => ({ ...state, suggestions: [suggestion] }));
  
  await mrBloomStore.handleSuggestion(suggestion);
  
  const stateAfter = get(mrBloomStore);
  
  expect(api.post).not.toHaveBeenCalled();
  expect(stateAfter.chatHistory).toEqual(initialState.chatHistory);
  expect(stateAfter.activeDraft).toBe(initialState.activeDraft);
  expect(stateAfter.sessionId).toBe(initialState.sessionId);
  expect(stateAfter.error).toBeNull();
});

test('editing a previewed draft immediately invalidates its token and hides Save state', async () => {
  const draft: TodayDraft = { type: 'today', planDate: '2026-09-20', timezone: 'UTC', windows: [], tasks: [] };
  mrBloomStore.update(state => ({ ...state, activeDraft: draft, preview: { preview_token: 'stale' } as any, previewMode: 'timeline' }));
  await mrBloomStore.applyPatch([{ op: 'set_windows', windows: [{ start: '10:00', end: '12:00' }] }]);
  expect(get(mrBloomStore).preview).toBeNull();
  expect(get(mrBloomStore).previewMode).toBe('today');
  expect(get(mrBloomStore).isDraftMutationPending).toBe(false);
  expect(api.post).not.toHaveBeenCalled();
});

test('a new draft clears a stale preview token', async () => {
  mrBloomStore.update(state => ({ ...state, preview: { preview_token: 'old' } as any, previewMode: 'timeline', sessionId: 'old-session' }));
  vi.mocked(api.post).mockResolvedValueOnce({
    reply: 'New draft', session_id: 'new-session',
    draft: { type: 'today', planDate: '2026-09-21', timezone: 'UTC', windows: [], tasks: [] },
    preview: { preview_token: 'server-preview-that-still-needs-review' }
  });
  await mrBloomStore.submitMessage('Make another plan');
  expect(get(mrBloomStore).preview).toBeNull();
  expect(get(mrBloomStore).previewMode).toBe('today');
});

test('successful save closes the local session and the next planning request starts a new one', async () => {
  const draft: TodayDraft = { type: 'today', planDate: '2026-09-20', timezone: 'UTC', windows: [], tasks: [] };
  mrBloomStore.update(state => ({ ...state, activeDraft: draft, preview: { preview_token: 'fresh' } as any, previewMode: 'timeline', sessionId: 'closed-session' }));
  vi.mocked(saveTodayPlan).mockResolvedValueOnce({} as any);
  await mrBloomStore.saveToday();
  expect(get(mrBloomStore).sessionId).toBeNull();
  expect(get(mrBloomStore).activeDraft).toBeNull();

  vi.mocked(api.post).mockResolvedValueOnce({ reply: 'Started', session_id: 'new-session', draft: null });
  await mrBloomStore.submitMessage('Plan tomorrow');
  expect(api.post).toHaveBeenLastCalledWith('/assistant/chat', expect.objectContaining({ session_id: null }));
  expect(get(mrBloomStore).sessionId).toBe('new-session');
});

test('a previous error does not block save retry and pending is always cleared', async () => {
  mrBloomStore.update(state => ({
    ...state, activeDraft: saveableDraft, preview: { preview_token: 'fresh' } as never,
    previewMode: 'timeline', error: 'old failure'
  }));
  vi.mocked(saveTodayPlan).mockRejectedValueOnce(new Error('network down'));
  await mrBloomStore.saveToday();
  expect(get(mrBloomStore).error).toBe('network down');
  expect(get(mrBloomStore).isSavePending).toBe(false);
  expect(get(mrBloomStore).activeDraft).toEqual(saveableDraft);

  vi.mocked(saveTodayPlan).mockResolvedValueOnce({} as never);
  await mrBloomStore.saveToday();
  expect(saveTodayPlan).toHaveBeenCalledTimes(2);
  expect(get(mrBloomStore).activeDraft).toBeNull();
});

test('duplicate save clicks make one request', async () => {
  let resolveSave!: (value: unknown) => void;
  vi.mocked(saveTodayPlan).mockReturnValueOnce(new Promise(resolve => { resolveSave = resolve; }) as never);
  mrBloomStore.update(state => ({
    ...state, activeDraft: saveableDraft, preview: { preview_token: 'fresh' } as never,
    previewMode: 'timeline'
  }));
  const first = mrBloomStore.saveToday();
  const second = mrBloomStore.saveToday();
  await vi.waitFor(() => expect(saveTodayPlan).toHaveBeenCalledTimes(1));
  resolveSave({});
  await Promise.all([first, second]);
});

test('PLAN_EXISTS opens confirmation; cancel preserves state; confirm replaces once', async () => {
  const { APIError } = await import('$lib/api');
  vi.mocked(saveTodayPlan)
    .mockRejectedValueOnce(new APIError(409, { detail: { code: 'PLAN_EXISTS' } }))
    .mockResolvedValueOnce({} as never);
  mrBloomStore.update(state => ({
    ...state, activeDraft: saveableDraft, preview: { preview_token: 'reviewed' } as never,
    previewMode: 'timeline'
  }));

  await mrBloomStore.saveToday();
  expect(get(mrBloomStore).needsReplace).toBe(true);
  expect(get(mrBloomStore).activeDraft).toEqual(saveableDraft);
  expect(get(mrBloomStore).preview?.preview_token).toBe('reviewed');

  mrBloomStore.cancelReplace();
  expect(get(mrBloomStore).needsReplace).toBe(false);
  expect(get(mrBloomStore).activeDraft).toEqual(saveableDraft);

  await mrBloomStore.confirmReplace();
  expect(saveTodayPlan).toHaveBeenLastCalledWith(null, 'reviewed', saveableDraft, true);
  expect(saveTodayPlan).toHaveBeenCalledTimes(2);
  expect(goto).toHaveBeenCalledOnce();
  expect(goto).toHaveBeenCalledWith('/today?date=2026-09-20');
});

test('milestone add uses the next free deterministic ID and edits preserve it', () => {
  mrBloomStore.update(state => ({
    ...state,
    activeDraft: {
      type: 'roadmap', goalId: 'g1', goalTitle: 'Goal', goalDescription: '', targetDate: '2026-12-31',
      milestones: [
        { id: 'm1', title: 'One', targetDate: '2026-10-01' },
        { id: 'm3', title: 'Three', targetDate: '2026-12-01' }
      ]
    },
    previewMode: 'roadmap'
  }));
  mrBloomStore.addMilestone();
  let roadmap = get(mrBloomStore).activeDraft;
  expect(roadmap?.type === 'roadmap' && roadmap.milestones.at(-1)?.id).toBe('m2');
  mrBloomStore.updateMilestone('m2', { title: 'Two' });
  roadmap = get(mrBloomStore).activeDraft;
  expect(roadmap?.type === 'roadmap' && roadmap.milestones.at(-1)).toMatchObject({ id: 'm2', title: 'Two' });
});

test('discarding a draft while Mr. Bloom is replying does not lock the composer', async () => {
  let resolveChat: (value: unknown) => void = () => {};
  vi.mocked(api.post).mockImplementationOnce(() => new Promise(resolve => { resolveChat = resolve; }));

  const pending = mrBloomStore.submitMessage('Plan my day');
  expect(get(mrBloomStore).isWaitingForResponse).toBe(true);

  mrBloomStore.discardDraft();
  resolveChat({ reply: 'Late reply', draft: null, suggestions: [], assumptions: [] });
  await pending;

  const state = get(mrBloomStore);
  expect(state.isWaitingForResponse).toBe(false);
  expect(state.chatHistory.some(message => message.content === 'Late reply')).toBe(false);
});

test('a failed reply that arrives after a save still releases the composer', async () => {
  let rejectChat: (reason: unknown) => void = () => {};
  vi.mocked(api.post).mockImplementationOnce(() => new Promise((_resolve, reject) => { rejectChat = reject; }));

  const pending = mrBloomStore.submitMessage('Plan my day');
  mrBloomStore.acceptDraft('Saved elsewhere.');
  rejectChat(new Error('Gateway timeout'));
  await pending;

  expect(get(mrBloomStore).isWaitingForResponse).toBe(false);
});

test('loadPlanForAdjustment converts persisted plan blocks into a TodayDraft', async () => {
  vi.mocked(api.get).mockResolvedValue({
    type: 'today',
    planDate: '2026-09-26',
    timezone: 'Asia/Ho_Chi_Minh',
    windows: [],
    tasks: [
      {
        id: 'task-abc',
        title: 'Study for exam',
        durationMin: 45,
        category: 'Learning',
        priority: 'URGENT',
        importance: 'CORE',
        estimateSource: 'USER',
        breakAfterMin: 10,
        deadline: '2026-09-26T18:00:00Z',
        schedulingType: 'FIXED',
        fixedStart: '2026-09-26T09:00:00+07:00',
        fixedEnd: '2026-09-26T09:45:00+07:00',
        dependencies: ['task-dep'],
        splittable: false,
        sourceTaskId: 'task-abc'
      }
    ],
    deferred_tasks: []
  });

  await mrBloomStore.loadPlanForAdjustment('2026-09-26', 'task-abc');
  const state = get(mrBloomStore);

  expect(api.get).toHaveBeenCalledWith('/today/draft?date=2026-09-26');
  expect(state.activeDraft?.type).toBe('today');
  expect(state.previewMode).toBe('today');
  expect(state.preview).toBeNull();
  expect(state.error).toBeNull();

  const draft = state.activeDraft as TodayDraft;
  expect(draft.planDate).toBe('2026-09-26');
  expect(draft.timezone).toBe('Asia/Ho_Chi_Minh');
  expect(draft.tasks).toHaveLength(1);
  expect(draft.tasks[0].id).not.toBeNull();
  expect(draft.tasks[0].title).toBe('Study for exam');
  expect(draft.tasks[0].durationMin).toBe(45);
  expect(draft.tasks[0].category).toBe('Learning');
  expect(draft.tasks[0].importance).toBe('CORE');
  expect(draft.tasks[0].breakAfterMin).toBe(10);
  expect(draft.tasks[0].priority).toBe('URGENT');
  expect(draft.tasks[0].schedulingType).toBe('FIXED');
  expect(draft.tasks[0].dependencies).toEqual(['task-dep']);
  
  // Chat message indicates task-specific adjustment
  expect(state.chatHistory.some(m => m.content.includes('Task selected for adjustment'))).toBe(true);
});

test('loadPlanForAdjustment ignores invalid taskId', async () => {
  vi.mocked(api.get).mockResolvedValue({
    type: 'today', planDate: '2026-09-26', timezone: 'UTC', windows: [],
    tasks: [{ id: 'task-abc', title: 'A task', durationMin: 30, category: 'Work', importance: 'CORE', priority: 'MEDIUM', schedulingType: 'FLEXIBLE', dependencies: [], splittable: false }],
    deferred_tasks: []
  });

  await mrBloomStore.loadPlanForAdjustment('2026-09-26', 'task-invalid');
  const state = get(mrBloomStore);
  
  expect(state.selectedTaskId).toBeNull();
  expect(state.chatHistory.some(m => m.content.includes('Task selected for adjustment'))).toBe(false);
});

test('loadPlanForAdjustment shows error when plan has no blocks', async () => {
  vi.mocked(api.get).mockResolvedValue({
    type: 'today', planDate: '2026-09-27', timezone: 'UTC', windows: [], tasks: [], deferred_tasks: []
  });

  await mrBloomStore.loadPlanForAdjustment('2026-09-27');
  const state = get(mrBloomStore);

  expect(state.activeDraft).toBeNull();
  expect(state.error).toBe('No plan found for this date.');
});

test('restoreLatestSession detects date param and loads plan for adjustment', async () => {
  window.history.replaceState({}, '', '/mr-bloom?date=2026-09-26&taskId=task-xyz');

  vi.mocked(api.get).mockResolvedValue({
    type: 'today', planDate: '2026-09-26', timezone: 'UTC', windows: [],
    tasks: [{
      id: 'task-xyz', sourceTaskId: 'task-xyz', title: 'Replanned task',
      durationMin: 30, category: 'Work', importance: 'OPTIONAL', priority: 'LOW',
      estimateSource: 'USER', breakAfterMin: 5, deadline: null, schedulingType: 'FLEXIBLE',
      fixedStart: null, fixedEnd: null, dependencies: [], splittable: false
    }],
    deferred_tasks: []
  });

  await mrBloomStore.restoreLatestSession();
  const state = get(mrBloomStore);

  // Should have loaded the plan, NOT fetched the latest session
  expect(api.get).toHaveBeenCalledWith('/today/draft?date=2026-09-26');
  expect(api.get).not.toHaveBeenCalledWith('/assistant/sessions/latest');
  expect(state.activeDraft?.type).toBe('today');
  expect(state.previewMode).toBe('today');

  // Cleanup URL
  window.history.replaceState({}, '', '/mr-bloom');
});

test('loads goal for adjustment and performs roadmap structural edits', async () => {
  const roadmapDraft = {
    type: 'roadmap',
    goalId: 'goal-123',
    goalTitle: 'Master React',
    targetDate: '2027-01-01',
    milestones: [
      { id: 'm1', title: 'Learn basics', targetDate: '2026-10-01', expectedOutcome: 'Done', status: 'PENDING' }
    ]
  };
  
  vi.mocked(api.get).mockResolvedValue(roadmapDraft);

  await mrBloomStore.loadGoalForAdjustment('goal-123');
  
  let state = get(mrBloomStore);
  expect(state.activeDraft?.type).toBe('roadmap');
  if (state.activeDraft?.type !== 'roadmap') throw new Error('draft type');
  expect(state.activeDraft.milestones).toHaveLength(1);
  
  // Add milestone
  mrBloomStore.addMilestone();
  state = get(mrBloomStore);
  if (state.activeDraft?.type !== 'roadmap') throw new Error('draft type');
  expect(state.activeDraft.milestones).toHaveLength(2);
  const newId = state.activeDraft.milestones[1].id;
  
  // Change milestone
  mrBloomStore.updateMilestone(newId!, { title: 'Advanced Topics' });
  state = get(mrBloomStore);
  if (state.activeDraft?.type !== 'roadmap') throw new Error('draft type');
  expect(state.activeDraft.milestones[1].title).toBe('Advanced Topics');
  
  // Remove milestone
  mrBloomStore.removeMilestone('m1');
  state = get(mrBloomStore);
  if (state.activeDraft?.type !== 'roadmap') throw new Error('draft type');
  expect(state.activeDraft.milestones).toHaveLength(1);
  expect(state.activeDraft.milestones[0].id).toBe(newId);
});

test('loads goal for adjustment and receives structural edits via chat', async () => {
  const initialDraft = {
    type: 'roadmap',
    goalId: 'goal-123',
    goalTitle: 'Master React',
    targetDate: '2027-01-01',
    milestones: [
      { id: 'm1', title: 'Learn basics', targetDate: '2026-10-01', expectedOutcome: 'Done', status: 'PENDING' },
      { id: 'm2', title: 'Advanced', targetDate: '2026-11-01', expectedOutcome: 'Done', status: 'PENDING' }
    ]
  };

  vi.mocked(api.get).mockResolvedValueOnce(initialDraft);
  
  await mrBloomStore.loadGoalForAdjustment('goal-123');
  
  let state = get(mrBloomStore);
  expect(state.activeDraft?.type).toBe('roadmap');
  expect((state.activeDraft as any).milestones).toHaveLength(2);

  // Chat structural edit: Add, change, remove, reorder
  const updatedDraft = {
    type: 'roadmap',
    goalId: 'goal-123',
    goalTitle: 'Master React',
    targetDate: '2027-01-01',
    milestones: [
      { id: 'm2', title: 'Advanced Changed', targetDate: '2026-11-01', expectedOutcome: 'Done', status: 'PENDING' },
      { id: '', title: 'New Milestone', targetDate: '2026-12-01', expectedOutcome: 'New', status: 'PENDING' }
    ]
  };

  vi.mocked(api.post).mockResolvedValueOnce({
    session_id: 'session-123',
    reply: 'Updated draft',
    draft: updatedDraft
  });

  await mrBloomStore.submitMessage('Reorder, remove m1, change m2, add new');
  
  state = get(mrBloomStore);
  expect((state.activeDraft as any).milestones).toHaveLength(2);
  expect((state.activeDraft as any).milestones[0].id).toBe('m2');
  expect((state.activeDraft as any).milestones[0].title).toBe('Advanced Changed');
  expect((state.activeDraft as any).milestones[1].title).toBe('New Milestone');
});

test('moving unfinished work to tomorrow reports what moved', async () => {
  vi.mocked(api.post).mockResolvedValueOnce({
    target_date: '2026-09-25', moved: [{ title: 'Viết báo cáo' }, { title: 'Đọc sách' }]
  });
  await mrBloomStore.handleSuggestion({ label: 'Move unfinished to tomorrow', action: 'CARRY_OVER_UNFINISHED' });
  expect(api.post).toHaveBeenCalledWith('/assistant/actions/CARRY_OVER_UNFINISHED', {});
  const state = get(mrBloomStore);
  expect(state.chatHistory.at(-1)?.content).toBe(
    "Moved 2 unfinished tasks to 2026-09-25. They will be in that day's draft when you plan it."
  );
  expect(state.suggestions).toEqual([]);
});
