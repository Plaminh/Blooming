import { beforeEach, describe, expect, it, vi } from 'vitest';
import { get } from 'svelte/store';
import {
  api, previewTodayPlan, saveTodayPlan, type TodayDraft, type TodayPreviewResponse
} from '$lib/api';
import { mrBloomStore } from './stores/mrBloomStore';

vi.mock('$lib/api', () => ({
  APIError: class APIError extends Error {
    constructor(public status: number, public detail: unknown) { super('API error'); }
  },
  api: { post: vi.fn(), get: vi.fn() },
  previewTodayPlan: vi.fn(),
  saveTodayPlan: vi.fn(),
  saveRoadmap: vi.fn()
}));

const draft: TodayDraft = {
  type: 'today', planDate: '2026-09-24', timezone: 'UTC',
  windows: [{ start: '09:00', end: '17:00' }],
  tasks: [{
    id: 'd1', title: 'Task 1', durationMin: 30, priority: 'MEDIUM', importance: 'CORE',
    category: null, estimateSource: 'USER', breakAfterMin: null, deadline: null,
    schedulingType: 'FLEXIBLE', fixedStart: null, fixedEnd: null, dependencies: [], splittable: false
  }], deferred_tasks: []
};

const preview = (token: string): TodayPreviewResponse => ({
  plan_date: draft.planDate, preview_token: token, timezone: 'UTC', status: 'PREVIEW',
  blocks: [], unscheduled_tasks: [], reasons: [], reality_check: 'COMFORTABLE'
});

describe('draft editor store integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mrBloomStore.set({
      chatHistory: [], isWaitingForResponse: false, activeDraft: draft,
      preview: preview('old'), previewMode: 'timeline', sessionId: 's1', degraded: null,
      suggestions: [], assumptions: [], needsReplace: false, isDraftMutationPending: false,
      isPreviewPending: false, isSavePending: false, error: null
    });
  });

  it('invalidates immediately, debounces the patch, previews once, and saves the refreshed token', async () => {
    vi.useFakeTimers();
    try {
      const edited = { ...draft, tasks: [{ ...draft.tasks[0], durationMin: 45 }] };
      vi.mocked(api.post).mockResolvedValue({ draft: edited });
      vi.mocked(previewTodayPlan).mockResolvedValue(preview('fresh'));
      vi.mocked(saveTodayPlan).mockResolvedValue({ ...preview('fresh') });

      mrBloomStore.updateTaskDuration('d1', 40);
      mrBloomStore.updateTaskDuration('d1', 45);
      const editing = get(mrBloomStore);
      expect(editing.preview).toBeNull();
      expect(editing.activeDraft?.type).toBe('today');
      if (editing.activeDraft?.type !== 'today') throw new Error('expected Today draft');
      expect(editing.activeDraft.tasks[0].durationMin).toBe(45);
      expect(editing.isDraftMutationPending).toBe(true);

      await vi.advanceTimersByTimeAsync(300);
      await vi.waitFor(() => expect(get(mrBloomStore).preview?.preview_token).toBe('fresh'));
      expect(api.post).toHaveBeenCalledTimes(1);
      expect(previewTodayPlan).toHaveBeenCalledTimes(1);

      await mrBloomStore.saveToday();
      expect(saveTodayPlan).toHaveBeenCalledWith('s1', 'fresh', edited, false);
      expect(get(mrBloomStore).activeDraft).toBeNull();
    } finally {
      vi.useRealTimers();
    }
  });

  it('clears pending state after a preview failure and keeps the edited draft', async () => {
    vi.mocked(api.post).mockResolvedValue({ draft });
    vi.mocked(previewTodayPlan).mockRejectedValue(new Error('preview failed'));
    await mrBloomStore.applyPatch([{ op: 'update_task', task_id: 'd1', importance: 'OPTIONAL' }]);
    await mrBloomStore.generateTimeline();
    expect(get(mrBloomStore).activeDraft).toEqual(draft);
    expect(get(mrBloomStore).isPreviewPending).toBe(false);
    expect(get(mrBloomStore).error).toBe('preview failed');
  });
});
