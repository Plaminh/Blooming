import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, fireEvent, screen, waitFor } from '@testing-library/svelte';
import PlanningWorkspace from './components/organisms/PlanningWorkspace.svelte';
import TodayPage from '../../../routes/(app)/today/+page.svelte';
import { api, previewTodayPlan, saveTodayPlan, getTodayPlan } from '$lib/api';

vi.mock('$lib/api', () => {
  class MockAPIError extends Error {
    status: number;
    constructor(msg: string, status: number) {
      super(msg);
      this.status = status;
    }
  }
  const mockApi = {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    put: vi.fn()
  };
  return {
    api: mockApi,
    getTodayPlan: vi.fn(),
    completeTodayTask: vi.fn(),
    replanToday: vi.fn(),
    startFocusSession: vi.fn(),
    logAssistantEvent: vi.fn(),

    APIError: MockAPIError,
    saveTodayPlan: vi.fn(),
    previewTodayPlan: vi.fn(),
    saveRoadmap: vi.fn()
  };
});

describe('Block 7 E2E-001: Simple Today Plan Happy Path', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.useFakeTimers({ toFake: ['Date'] });
    vi.setSystemTime(new Date('2026-09-22T09:00:00Z'));
    HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
    HTMLDialogElement.prototype.close = function () {
      this.removeAttribute('open');
      this.dispatchEvent(new Event('close'));
    };

    let planSaved = false;

    vi.mocked(api.get).mockImplementation(async (url: string) => {
      if (url === '/me/settings') return { default_focus_minutes: 50, default_break_minutes: 10 };
      const parsedUrl = new URL(url, "http://localhost");
      throw new Error(`Unexpected GET: ${url}`);
    });

        vi.mocked(previewTodayPlan).mockResolvedValue({
      preview_token: 'pt1',
      plan_date: '2026-09-22',
      status: 'DRAFT',
      timezone: 'UTC',
      unscheduled_tasks: [],
      reasons: [],
      reality_check: null,
      blocks: [
        { id: 'b1', draft_task_id: 'd1', title: 'Today I need to read chapter 3 for', block_type: 'TASK', estimated_duration_minutes: 45, planned_start_at: '2026-09-22T06:00:00Z', planned_end_at: '2026-09-22T06:45:00Z', status: 'DRAFT', task_id: null, description: null, category: null, importance: null, preferred_break_duration_minutes: null, source: null, position: 0, is_locked: false },
        { id: 'b2', draft_task_id: null, estimated_duration_minutes: null, title: 'Break', block_type: 'BREAK', planned_start_at: '2026-09-22T06:45:00Z', planned_end_at: '2026-09-22T06:50:00Z', status: 'DRAFT', task_id: null, description: null, category: null, importance: null, preferred_break_duration_minutes: null, source: null, position: 0, is_locked: false },
        { id: 'b3', draft_task_id: 'd2', title: 'review flashcards for', block_type: 'TASK', estimated_duration_minutes: 30, planned_start_at: '2026-09-22T06:50:00Z', planned_end_at: '2026-09-22T07:20:00Z', status: 'DRAFT', task_id: null, description: null, category: null, importance: null, preferred_break_duration_minutes: null, source: null, position: 0, is_locked: false }
      ] 
    });

    vi.mocked(saveTodayPlan).mockImplementation(async () => {
      planSaved = true;
      return { plan_date: '2026-09-22', status: 'ACTIVE', timezone: 'UTC', unscheduled_tasks: [], reasons: [], reality_check: null, blocks: [] };
    });

    vi.mocked(getTodayPlan).mockImplementation(async (date) => {
      if (!planSaved) return { plan_date: '2026-09-22', status: 'NO_PLAN', timezone: 'UTC', unscheduled_tasks: [], reasons: [], reality_check: null, blocks: [] };
      return { plan_date: '2026-09-22', status: 'ACTIVE', timezone: 'UTC', unscheduled_tasks: [], reasons: [], reality_check: null, blocks: [] };
    });

    vi.mocked(api.post).mockImplementation(async (url: string, payload: unknown) => {
      if (url === '/assistant/chat') {

        return {
          reply: 'I have created a draft. Please review.',
          session_id: 's1',
          intent: 'PLAN_DAY',
          tier: 'PARSER',
          draft: {
            type: 'today',
            planDate: '2026-09-22',
            timezone: 'UTC',
            windows: [{ start: '06:00', end: '22:00' }],
            tasks: [
              { id: 'd1', title: 'Today I need to read chapter 3 for', durationMin: 45 },
              { id: 'd2', title: 'review flashcards for', durationMin: 30 }
            ]
          },
          preview: null,
          suggestions: []
        };
      }
      
      
      throw new Error(`Unexpected POST: ${url}`);
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('E2E-001: Enter message -> draft -> preview -> Save -> verify Today tasks', async () => {
    // 1. Mount MrBloom Planning Workspace
    const bloom = render(PlanningWorkspace);
    
    // Enter the message and send
    const input = screen.getByPlaceholderText(/Choose what you want to plan first/i);
    await fireEvent.input(input, { target: { value: 'Today I need to read chapter 3 for 45 minutes and review flashcards for 30 minutes.' } });
    
    const sendButton = screen.getByRole('button', { name: 'Send' });
    await waitFor(() => expect(sendButton).not.toBeDisabled());
    await fireEvent.click(sendButton);

    // See draft
    await waitFor(() => {
      expect(screen.getByDisplayValue('Today I need to read chapter 3 for')).toBeInTheDocument();
      expect(screen.getByDisplayValue('review flashcards for')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /GENERATE TIMELINE/i })).toBeInTheDocument();
    });

    // Verify Today is unchanged before Save
    const todayBefore = render(TodayPage);
    await waitFor(() => {
      // It should display empty state for Today
      expect(todayBefore.container.textContent).toMatch(/No tasks scheduled for this day/i);
    });
    todayBefore.unmount();

    // Click Generate Timeline
    const generateBtn = screen.getByRole('button', { name: /GENERATE TIMELINE/i });
    await fireEvent.click(generateBtn);

    // Wait for preview response and SAVE button
    await waitFor(() => {
      expect(previewTodayPlan).toHaveBeenCalledWith(expect.any(Object));
      expect(screen.getByRole('button', { name: /^SAVE$/i })).toBeInTheDocument();
    });

    // Click Save inside MrBloom right panel
    const saveButton = screen.getByRole('button', { name: /^SAVE$/i });
    await fireEvent.click(saveButton);

    // Wait for the save post request to complete
    await waitFor(() => {
      expect(saveTodayPlan).toHaveBeenCalledWith(expect.anything(), expect.anything(), expect.any(Object), false);
    });
    
    // Open/reload Today -> Verify the two persisted tasks
    const todayAfter = render(TodayPage);
    await waitFor(() => {
      expect(todayAfter.container.textContent).toMatch(/Today I need to read chapter 3 for/);
      expect(todayAfter.container.textContent).toMatch(/review flashcards for/);
    });
  });
});
