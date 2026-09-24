import { describe, it, expect, vi, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { mrBloomStore } from '$lib/features/mr-bloom/stores/mrBloomStore';
import { api } from '$lib/api';
import type { TodayPreviewResponse, TodayDraft, TaskDraft, RepairSuggestion, PatchOp } from '$lib/api';

vi.mock('$lib/api', () => ({
  api: {
    post: vi.fn(),
  },
  previewTodayPlan: async (draft: import('$lib/api').TodayDraft) => await import('$lib/api').then(m => m.api.post('/today/preview', { draft })),
}));

const baseTask = (overrides: Partial<TaskDraft> = {}): TaskDraft => ({
  id: 'd1', title: 'Core task', durationMin: 60, priority: 'HIGH', importance: 'CORE',
  category: null, estimateSource: 'USER', breakAfterMin: null, deadline: null,
  schedulingType: 'FLEXIBLE', fixedStart: null, fixedEnd: null, dependencies: [], splittable: false,
  ...overrides,
});

const optionalTask = (overrides: Partial<TaskDraft> = {}): TaskDraft => ({
  id: 'd2', title: 'Optional reading', durationMin: 45, priority: 'LOW', importance: 'OPTIONAL',
  category: null, estimateSource: 'RULE', breakAfterMin: null, deadline: null,
  schedulingType: 'FLEXIBLE', fixedStart: null, fixedEnd: null, dependencies: [], splittable: false,
  ...overrides,
});

const overloadedPreview: TodayPreviewResponse = {
  plan_date: '2026-09-20',
  status: 'PREVIEW',
  timezone: 'UTC',
  preview_token: 'tok-old',
  reality_check: 'OVERLOADED',
  blocks: [],
  unscheduled_tasks: [{ draft_task_id: 'd2', title: 'Optional reading', reason: 'INSUFFICIENT_TIME' } ],
  reasons: [{ code: 'INSUFFICIENT_TIME', task_id: 'd2' }],
  suggestions: [{ label: 'Remove optional: Optional reading', patch: [{ op: 'remove_task', task_id: 'd2' }] }]
};

const comfortablePreview: TodayPreviewResponse = {
  plan_date: '2026-09-20',
  status: 'PREVIEW',
  timezone: 'UTC',
  preview_token: 'tok-new',
  reality_check: 'COMFORTABLE',
  blocks: [],
  unscheduled_tasks: [],
  reasons: [],
  suggestions: []
};

const validDraft = (tasks: TaskDraft[]): TodayDraft => ({
  type: 'today',
  planDate: '2026-09-20',
  timezone: 'UTC',
  windows: [{ start: '09:00', end: '10:00' }],
  tasks,
  deferred_tasks: []
});

describe('E2E-003: Overloaded suggestion flow', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    mrBloomStore.set({
      chatHistory: [], isWaitingForResponse: false, activeDraft: null, preview: null, previewMode: 'placeholder',
      sessionId: null, degraded: null, suggestions: [], assumptions: [], needsReplace: false,
      isDraftMutationPending: false, isPreviewPending: false, isSavePending: false, error: null,
    });
  });

  const setupOverloaded = async () => {
    mrBloomStore.update(state => ({
      ...state,
      activeDraft: validDraft([baseTask(), optionalTask()])
    }));

    vi.mocked(api.post).mockImplementation(async (url: string) => {
      if (url === '/today/preview') return overloadedPreview;
      throw new Error("Unexpected call to " + url);
    });
    await mrBloomStore.generateTimeline();
  };

  it('exercises full production suggestion flow successfully', async () => {
    await setupOverloaded();
    let state = get(mrBloomStore);
    const suggestion = state.preview?.suggestions?.[0] as RepairSuggestion;
    expect(suggestion).toBeDefined();

    const patchedDraft = validDraft([baseTask()]);

    vi.mocked(api.post).mockImplementation(async (url: string, body: { draft: TodayDraft; ops?: PatchOp[] }) => {
      if (url === '/assistant/apply-patch') {
        expect(body.ops).toEqual(suggestion.patch);
        return { draft: patchedDraft };
      }
      if (url === '/today/preview') {
        return comfortablePreview;
      }
      throw new Error("Unexpected call to " + url);
    });

    const promise = mrBloomStore.applySuggestionAndRepreview(suggestion);
    
    // immediate states
    state = get(mrBloomStore);
    expect(state.isDraftMutationPending).toBe(true);

    await promise;

    state = get(mrBloomStore);
    expect(state.preview?.preview_token).toBe('tok-new');
    expect(state.preview?.reality_check).toBe('COMFORTABLE');
    expect(state.isDraftMutationPending).toBe(false);
    expect(state.isPreviewPending).toBe(false);
    
    const calls = vi.mocked(api.post).mock.calls;
    expect(calls.some((c: Parameters<typeof api.post>) => c[0] === '/today/save')).toBe(false);
  });

  it('handles apply-patch failure safely', async () => {
    await setupOverloaded();
    const state = get(mrBloomStore);
    const suggestion = state.preview?.suggestions?.[0] as RepairSuggestion;
    
    vi.mocked(api.post).mockImplementation(async (url: string) => {
      if (url === '/assistant/apply-patch') throw new Error("Patch failed");
      throw new Error("Unexpected call to " + url);
    });

    await mrBloomStore.applySuggestionAndRepreview(suggestion);
    
    const finalState = get(mrBloomStore);
    expect(finalState.error).toContain("Patch failed");
    expect(finalState.isDraftMutationPending).toBe(false);
    // Did not call preview
    const calls = vi.mocked(api.post).mock.calls.filter((c: Parameters<typeof api.post>) => c[0] === '/today/preview');
    expect(calls.length).toBe(1); // Only the initial one from setupOverloaded
    // No save
    expect(vi.mocked(api.post).mock.calls.some((c: Parameters<typeof api.post>) => c[0] === '/today/save')).toBe(false);
  });

  it('handles re-preview failure safely', async () => {
    await setupOverloaded();
    const state = get(mrBloomStore);
    const suggestion = state.preview?.suggestions?.[0] as RepairSuggestion;
    
    const patchedDraft = validDraft([baseTask()]);

    vi.mocked(api.post).mockImplementation(async (url: string) => {
      if (url === '/assistant/apply-patch') return { draft: patchedDraft };
      if (url === '/today/preview') throw new Error("Preview failed");
      throw new Error("Unexpected call to " + url);
    });

    await mrBloomStore.applySuggestionAndRepreview(suggestion);
    
    const finalState = get(mrBloomStore);
    expect(finalState.activeDraft).toEqual(patchedDraft);
    expect(finalState.preview).toBeNull();
    expect(finalState.error).toContain("Preview failed");
    expect(finalState.isPreviewPending).toBe(false);
    expect(vi.mocked(api.post).mock.calls.some((c: Parameters<typeof api.post>) => c[0] === '/today/save')).toBe(false);
  });
  
  it('rejects stale or unchanged preview token safely', async () => {
    await setupOverloaded();
    const state = get(mrBloomStore);
    const suggestion = state.preview?.suggestions?.[0] as RepairSuggestion;
    
    const patchedDraft = validDraft([baseTask()]);

    vi.mocked(api.post).mockImplementation(async (url: string) => {
      if (url === '/assistant/apply-patch') return { draft: patchedDraft };
      if (url === '/today/preview') return overloadedPreview; // Same stale token
      throw new Error("Unexpected call to " + url);
    });

    await mrBloomStore.applySuggestionAndRepreview(suggestion);
    
    const finalState = get(mrBloomStore);
    expect(finalState.activeDraft).toEqual(patchedDraft);
    expect(finalState.preview).toBeNull();
    expect(finalState.error).toContain("Stale preview token received.");
    expect(finalState.isPreviewPending).toBe(false);
    expect(vi.mocked(api.post).mock.calls.some((c: Parameters<typeof api.post>) => c[0] === '/today/save')).toBe(false);
  });
  
  it('rejects missing preview token safely', async () => {
    await setupOverloaded();
    const state = get(mrBloomStore);
    const suggestion = state.preview?.suggestions?.[0] as RepairSuggestion;
    
    const patchedDraft = validDraft([baseTask()]);

    vi.mocked(api.post).mockImplementation(async (url: string) => {
      if (url === '/assistant/apply-patch') return { draft: patchedDraft };
      if (url === '/today/preview') return { ...comfortablePreview, preview_token: undefined }; 
      throw new Error("Unexpected call to " + url);
    });

    await mrBloomStore.applySuggestionAndRepreview(suggestion);
    
    const finalState = get(mrBloomStore);
    expect(finalState.activeDraft).toEqual(patchedDraft);
    expect(finalState.preview).toBeNull();
    expect(finalState.error).toContain("Stale preview token received.");
    expect(finalState.isPreviewPending).toBe(false);
  });

  it('ignores double clicks while pending', async () => {
    await setupOverloaded();
    const state = get(mrBloomStore);
    const suggestion = state.preview?.suggestions?.[0] as RepairSuggestion;
    
    let resolvePatch: (v: unknown) => void = () => {};
    const patchPromise = new Promise(r => resolvePatch = r);
    vi.mocked(api.post).mockImplementation(async (url: string) => {
      if (url === '/assistant/apply-patch') {
        await patchPromise;
        return { draft: validDraft([baseTask()]) };
      }
      if (url === '/today/preview') return comfortablePreview;
    });

    const p1 = mrBloomStore.applySuggestionAndRepreview(suggestion);
    const p2 = mrBloomStore.applySuggestionAndRepreview(suggestion);
    
    resolvePatch(null);
    await Promise.all([p1, p2]);

    const patchCalls = vi.mocked(api.post).mock.calls.filter((c: Parameters<typeof api.post>) => c[0] === '/assistant/apply-patch');
    expect(patchCalls.length).toBe(1); // Only called once!
  });
});
