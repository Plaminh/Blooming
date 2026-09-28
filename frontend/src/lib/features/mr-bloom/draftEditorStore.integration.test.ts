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
      suggestions: [], assumptions: [], needsReplace: false, selectedTaskId: null, isDraftMutationPending: false,
      isPreviewPending: false, isSavePending: false, error: null
    });
  });

  it('keeps duration edits local until explicit generation, then saves the refreshed token', async () => {
    const edited = { ...draft, tasks: [{ ...draft.tasks[0], durationMin: 45 }] };
    vi.mocked(previewTodayPlan).mockResolvedValue(preview('fresh'));
    vi.mocked(saveTodayPlan).mockResolvedValue({
      plan_date: draft.planDate, timezone: 'UTC', status: 'ACTIVE',
      blocks: [], unscheduled_tasks: [], reasons: [], reality_check: 'COMFORTABLE'
    });

    mrBloomStore.updateTaskDuration('d1', 40);
    mrBloomStore.updateTaskDuration('d1', 45);
    const editing = get(mrBloomStore);
    expect(editing.preview).toBeNull();
    expect(editing.previewMode).toBe('today');
    expect(editing.activeDraft).toEqual(edited);
    expect(previewTodayPlan).not.toHaveBeenCalled();

    await mrBloomStore.generateTimeline();
    expect(previewTodayPlan).toHaveBeenCalledTimes(1);
    expect(previewTodayPlan).toHaveBeenCalledWith(edited);
    expect(get(mrBloomStore).preview?.preview_token).toBe('fresh');

    await mrBloomStore.saveToday();
    expect(saveTodayPlan).toHaveBeenCalledWith('s1', 'fresh', edited, false);
    expect(get(mrBloomStore).activeDraft).toBeNull();
  });

  it('preserves sequential title and importance edits without automatic preview', async () => {
    mrBloomStore.updateTaskTitle('d1', 'R');
    mrBloomStore.updateTaskTitle('d1', 'Review');
    mrBloomStore.updateTaskTitle('d1', 'Review algorithms');
    await mrBloomStore.updateTaskImportance('d1', 'OPTIONAL');

    const editing = get(mrBloomStore);
    expect(editing.preview).toBeNull();
    expect(editing.previewMode).toBe('today');
    expect(editing.activeDraft?.type).toBe('today');
    if (editing.activeDraft?.type !== 'today') throw new Error('expected Today draft');
    expect(editing.activeDraft.tasks[0]).toMatchObject({
      id: 'd1', title: 'Review algorithms', durationMin: 30, importance: 'OPTIONAL'
    });
    expect(api.post).not.toHaveBeenCalled();
    expect(previewTodayPlan).not.toHaveBeenCalled();
  });

  it('only activates the latest overlapping explicit preview response', async () => {
    let resolveFirst!: (value: TodayPreviewResponse) => void;
    vi.mocked(previewTodayPlan)
      .mockReturnValueOnce(new Promise(resolve => { resolveFirst = resolve; }))
      .mockResolvedValueOnce(preview('latest'));

    const first = mrBloomStore.generateTimeline();
    mrBloomStore.updateTaskTitle('d1', 'Review algorithms');
    const second = mrBloomStore.generateTimeline();
    await second;
    resolveFirst(preview('stale'));
    await first;

    expect(previewTodayPlan).toHaveBeenCalledTimes(2);
    expect(get(mrBloomStore).preview?.preview_token).toBe('latest');
    expect(get(mrBloomStore).previewMode).toBe('timeline');
  });

  it('clears pending state after a preview failure and keeps the edited draft', async () => {
    vi.mocked(api.post).mockResolvedValue({ draft });
    vi.mocked(previewTodayPlan).mockRejectedValue(new Error('preview failed'));
    await mrBloomStore.applyPatch([{ op: 'update_task', task_id: 'd1', importance: 'OPTIONAL' }]);
    await mrBloomStore.generateTimeline();
    expect(get(mrBloomStore).activeDraft).toEqual({
      ...draft, tasks: [{ ...draft.tasks[0], importance: 'OPTIONAL' }]
    });
    expect(get(mrBloomStore).isPreviewPending).toBe(false);
    expect(get(mrBloomStore).error).toBe('preview failed');
  });
});
