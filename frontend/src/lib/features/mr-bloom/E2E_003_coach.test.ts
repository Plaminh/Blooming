import { beforeEach, describe, expect, it, vi } from 'vitest';
import { get } from 'svelte/store';
import { api, previewTodayPlan, type TaskDraft, type TodayDraft, type TodayPreviewResponse } from '$lib/api';
import { mrBloomStore } from './stores/mrBloomStore';

vi.mock('$lib/api', () => ({
  api: { post: vi.fn() }, previewTodayPlan: vi.fn(), saveTodayPlan: vi.fn(), saveRoadmap: vi.fn(),
  APIError: class APIError extends Error {}
}));

const task = (id: string, importance: 'CORE' | 'OPTIONAL'): TaskDraft => ({
  id, title: id === 'd1' ? 'Core task' : 'Optional reading', durationMin: 45,
  priority: 'MEDIUM', importance, category: null, estimateSource: 'USER', breakAfterMin: null,
  deadline: null, schedulingType: 'FLEXIBLE', fixedStart: null, fixedEnd: null,
  dependencies: [], splittable: false
});
const draft: TodayDraft = {
  type: 'today', planDate: '2026-09-20', timezone: 'UTC',
  windows: [{ start: '09:00', end: '12:00' }],
  tasks: [task('d1', 'CORE'), task('d2', 'OPTIONAL')], deferred_tasks: []
};
const preview = (token: string): TodayPreviewResponse => ({
  plan_date: draft.planDate, status: 'PREVIEW', timezone: 'UTC', preview_token: token,
  reality_check: 'COMFORTABLE', blocks: [], unscheduled_tasks: [], reasons: [], suggestions: []
});

describe('E2E-003: repair suggestions follow manual regeneration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mrBloomStore.set({
      chatHistory: [], isWaitingForResponse: false, activeDraft: draft,
      preview: preview('old'), previewMode: 'timeline', sessionId: 's1', degraded: null,
      suggestions: [], assumptions: [], needsReplace: false, selectedTaskId: null, isDraftMutationPending: false,
      isPreviewPending: false, isSavePending: false, error: null
    });
  });

  it('applies a repair locally and waits for explicit Generate Timeline', async () => {
    await mrBloomStore.applyPatch([{ op: 'remove_task', task_id: 'd2' }]);
    const edited = get(mrBloomStore);
    expect(edited.activeDraft?.type === 'today' && edited.activeDraft.tasks.map(item => item.id)).toEqual(['d1']);
    expect(edited.preview).toBeNull();
    expect(edited.previewMode).toBe('today');
    expect(api.post).not.toHaveBeenCalled();
    expect(previewTodayPlan).not.toHaveBeenCalled();

    vi.mocked(previewTodayPlan).mockResolvedValue(preview('fresh'));
    await mrBloomStore.generateTimeline();
    expect(previewTodayPlan).toHaveBeenCalledTimes(1);
    expect(get(mrBloomStore).preview?.preview_token).toBe('fresh');
  });

  it('does not automatically regenerate for repeated local edits', async () => {
    await mrBloomStore.applyPatch([{ op: 'remove_task', task_id: 'd2' }]);
    mrBloomStore.updateTaskDuration('d1', 60);
    mrBloomStore.updateTaskTitle('d1', 'Renamed core task');
    expect(previewTodayPlan).not.toHaveBeenCalled();
    expect(api.post).not.toHaveBeenCalled();
    const current = get(mrBloomStore).activeDraft;
    expect(current?.type === 'today' && current.tasks[0]).toMatchObject({
      id: 'd1', title: 'Renamed core task', durationMin: 60
    });
  });
});
