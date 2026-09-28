import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { get } from 'svelte/store';
import PlanningWorkspace from './components/organisms/PlanningWorkspace.svelte';
import { mrBloomStore } from './stores/mrBloomStore';
import { api, previewTodayPlan, saveTodayPlan } from '$lib/api';

vi.mock('$lib/api', () => {
  class MockAPIError extends Error { constructor(message: string, public status: number) { super(message); } }
  const mockApi = { get: vi.fn(), post: vi.fn(), patch: vi.fn(), put: vi.fn() };
  return {
    api: mockApi,
    getTodayPlan: vi.fn(),
    completeTodayTask: vi.fn(),
    replanToday: vi.fn(),
    startFocusSession: vi.fn(),
    logAssistantEvent: vi.fn(),
 APIError: MockAPIError,
    previewTodayPlan: vi.fn(),
    saveTodayPlan: vi.fn(),
    saveRoadmap: vi.fn()
  };
});

const task = (overrides: Record<string, unknown> = {}) => ({
  id: 'd1', title: 'Study algorithms', durationMin: 60, priority: 'MEDIUM', importance: 'CORE',
  category: null, estimateSource: 'USER', breakAfterMin: null, deadline: null,
  schedulingType: 'FLEXIBLE', fixedStart: null, fixedEnd: null, dependencies: [], splittable: false,
  ...overrides
});
const draft = (overrides: Record<string, unknown> = {}) => ({
  type: 'today', planDate: '2026-09-22', timezone: 'Asia/Ho_Chi_Minh',
  windows: [{ start: '06:00', end: '22:00' }], tasks: [task()], ...overrides
});

async function send(chatResponse: Record<string, unknown>, message = 'Plan my day') {
  vi.mocked(api.post).mockImplementation(async (url: string) => {
    if (url === '/assistant/chat') return chatResponse;
    throw new Error(`Unexpected POST: ${url}`);
  });
  render(PlanningWorkspace);
  await fireEvent.input(screen.getByPlaceholderText(/Choose what you want to plan first/i), { target: { value: message } });
  await fireEvent.click(screen.getByRole('button', { name: 'Send' }));
}

describe('Block 9 E2E: time constraints and lifecycle', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    mrBloomStore.set({
      chatHistory: [], isWaitingForResponse: false, activeDraft: null, preview: null,
      previewMode: 'placeholder', sessionId: null, degraded: null, suggestions: [], assumptions: [],
      needsReplace: false, selectedTaskId: null, isDraftMutationPending: false, isPreviewPending: false, isSavePending: false, error: null
    });
    vi.mocked(api.get).mockImplementation(async (url: string) => {
      if (url === '/me/settings') return { default_focus_minutes: 50, default_break_minutes: 10 };
      throw new Error(`Unexpected GET: ${url}`);
    });
  });

  it('PS-006 renders a fixed start without inventing a fixed end', async () => {
    await send({ reply: 'Draft ready', session_id: 's1', draft: draft({ tasks: [task({ fixedStart: '14:00', schedulingType: 'FIXED' })] }) });
    await waitFor(() => expect((screen.getByLabelText('Start time') as HTMLInputElement).value).toBe('14:00'));
    expect((screen.getByLabelText('End time') as HTMLInputElement).value).toBe('');
  });

  it('PS-008 renders a deadline as a flexible constraint', async () => {
    await send({ reply: 'Draft ready', session_id: 's1', draft: draft({ tasks: [task({ deadline: '17:00', schedulingType: 'FLEXIBLE' })] }) });
    await waitFor(() => expect((screen.getByLabelText('Deadline') as HTMLInputElement).value).toBe('17:00'));
    expect((get(mrBloomStore).activeDraft as import('$lib/api/types').TodayDraft).tasks[0].schedulingType).toBe('FLEXIBLE');
  });

  it('PS-009 renders explicit availability without turning it into a task', async () => {
    await send({ reply: 'Draft ready', session_id: 's1', draft: draft({ windows: [{ start: '18:00', end: '21:00' }] }) });
    await waitFor(() => expect(screen.getByText(/18:00.*21:00/)).toBeInTheDocument());
    expect(screen.getAllByDisplayValue('Study algorithms')).toHaveLength(1);
  });

  it('PS-010 renders a normalized budget-only draft with no fake task', async () => {
    await send({
      reply: 'Tell me what to schedule', session_id: 's1', draft: draft({ tasks: [] }),
      assumptions: [{ id: 'budget', kind: 'BUDGET', text: 'Normalized budget: 120 minutes', task_id: null }]
    });
    await waitFor(() => expect(screen.getByText(/Time budget.*120 minutes/)).toBeInTheDocument());
    expect(screen.getByText(/Please add tasks/)).toBeInTheDocument();
  });

  it('PS-015 keeps tomorrow as the draft plan date', async () => {
    await send({ reply: 'Tomorrow draft', session_id: 's1', draft: draft({ planDate: '2026-09-23' }) }, 'Tomorrow, study algorithms for 60 min');
    await waitFor(() => expect(get(mrBloomStore).activeDraft?.type).toBe('today'));
    expect((get(mrBloomStore).activeDraft as import('$lib/api/types').TodayDraft).planDate).toBe('2026-09-23');
  });

  it('invalid interval shows clarification and never exposes preview or Save', async () => {
    await send({ reply: 'The fixed end must be after the fixed start.', session_id: 's1', draft: null, preview: null });
    await waitFor(() => expect(screen.getByText(/fixed end must be after/i)).toBeInTheDocument());
    expect(api.post).not.toHaveBeenCalledWith('/today/preview', expect.anything());
    expect(screen.queryByRole('button', { name: /^SAVE$/i })).not.toBeInTheDocument();
  });

  it('editing after preview invalidates the token and the scheduler receives the edited draft', async () => {
    const initial = draft({ tasks: [task({ fixedStart: '14:00', fixedEnd: '15:00', schedulingType: 'FIXED' })] });
    const patched = { ...initial, tasks: [task({ fixedStart: null, fixedEnd: null, schedulingType: 'FLEXIBLE' })] };
        vi.mocked(previewTodayPlan).mockResolvedValue({ preview_token: 'token', blocks: [], status: 'DRAFT', plan_date: '2026-09-22', timezone: 'UTC', unscheduled_tasks: [], reasons: [], reality_check: null } as import('$lib/api/types').TodayPreviewResponse);
    vi.mocked(api.post).mockImplementation(async (url: string, payload: unknown) => {
      if (url === '/assistant/chat') return { reply: 'Draft ready', session_id: 's1', draft: initial };
      throw new Error(`Unexpected POST: ${url}: ${JSON.stringify(payload)}`);
    });
    render(PlanningWorkspace);
    await fireEvent.input(screen.getByPlaceholderText(/Choose what you want to plan first/i), { target: { value: 'Fixed interval' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Send' }));
    await waitFor(() => expect(screen.getByLabelText('Start time')).toBeInTheDocument());
    await fireEvent.click(screen.getByRole('button', { name: /GENERATE TIMELINE/i }));
    await waitFor(() => expect(screen.getByRole('button', { name: /^SAVE$/i })).toBeInTheDocument());
    await fireEvent.click(screen.getByRole('button', { name: 'BACK TO TASKS' }));
    await fireEvent.click(screen.getByRole('button', { name: 'Clear fixed time' }));
    await waitFor(() => expect(screen.queryByRole('button', { name: /^SAVE$/i })).not.toBeInTheDocument());
    expect(get(mrBloomStore).preview).toBeNull();
    await fireEvent.click(screen.getByRole('button', { name: /GENERATE TIMELINE/i }));
    await waitFor(() => expect(api.post).toHaveBeenLastCalledWith('/today/preview', { draft: patched }));
  });

  it('successful save clears the closed session before the next planning request', async () => {
    const current = draft();
    mrBloomStore.update(state => ({ ...state, activeDraft: current as import('$lib/api/types').TodayDraft, sessionId: 'closed', previewMode: 'timeline', preview: { preview_token: 'pt' } as import('$lib/api/types').TodayPreviewResponse }));
        vi.mocked(saveTodayPlan).mockResolvedValue({ status: 'ACTIVE', blocks: [], plan_date: '2026-09-22', timezone: 'UTC', unscheduled_tasks: [], reasons: [], reality_check: null } as import('$lib/api/types').TodayResponse);
    vi.mocked(api.post).mockImplementation(async (url: string) => {
      if (url === '/assistant/chat') return { reply: 'New session', session_id: 'fresh', draft: null };
      throw new Error(`Unexpected POST: ${url}`);
    });
    await mrBloomStore.saveToday();
    expect(get(mrBloomStore).sessionId).toBeNull();
    await mrBloomStore.submitMessage('Plan another day');
    expect(api.post).toHaveBeenLastCalledWith('/assistant/chat', expect.objectContaining({ session_id: null }));
  });
});
