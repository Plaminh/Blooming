import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, fireEvent, screen, waitFor } from '@testing-library/svelte';
import PlanningWorkspace from './components/organisms/PlanningWorkspace.svelte';
import TodayPage from '../../../routes/(app)/today/+page.svelte';
import { api } from '$lib/api';

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
    APIError: MockAPIError,
    saveTodayPlan: async (sId: string, token: string, draft: any, replace: boolean) => mockApi.post('/today/save', { session_id: sId, preview_token: token, draft, replace_existing: replace }),
    previewTodayPlan: async (draft: any) => mockApi.post('/today/preview', { draft }),
    saveRoadmap: async (sId: string, draft: any) => mockApi.post('/goals/from-roadmap', { session_id: sId, draft })
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

    (api.get as any).mockImplementation(async (url: string) => {
      if (url === '/me/settings') return { default_focus_minutes: 50, default_break_minutes: 10 };
      const parsedUrl = new URL(url, "http://localhost");
      if (parsedUrl.pathname === '/today') {
        if (!planSaved) {
          return { plan_date: '2026-09-22', status: 'NO_PLAN', timezone: 'UTC', blocks: [] };
        } else {
          return {
            plan_date: '2026-09-22',
            status: 'ACTIVE',
            timezone: 'UTC',
            blocks: [
              {
                id: 'b1',
                task_id: 't1',
                title: 'Today I need to read chapter 3 for',
                planned_start_at: '2026-09-22T06:00:00Z',
                planned_end_at: '2026-09-22T06:45:00Z',
                status: 'PLANNED',
                block_type: 'TASK'
              },
              {
                id: 'b2',
                task_id: 't2',
                title: 'review flashcards for',
                planned_start_at: '2026-09-22T06:50:00Z',
                planned_end_at: '2026-09-22T07:20:00Z',
                status: 'PLANNED',
                block_type: 'TASK'
              }
            ]
          };
        }
      }
      throw new Error(`Unexpected GET: ${url}`);
    });

    (api.post as any).mockImplementation(async (url: string, payload: any) => {
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
      if (url === '/today/preview') {
        return {
          preview_token: 'pt1',
          blocks: [
            { id: 'b1', draft_task_id: 'd1', title: 'Today I need to read chapter 3 for', block_type: 'TASK', estimated_duration_minutes: 45, planned_start_at: '2026-09-22T06:00:00Z', planned_end_at: '2026-09-22T06:45:00Z' },
            { id: 'b2', title: 'Break', block_type: 'BREAK', planned_start_at: '2026-09-22T06:45:00Z', planned_end_at: '2026-09-22T06:50:00Z' },
            { id: 'b3', draft_task_id: 'd2', title: 'review flashcards for', block_type: 'TASK', estimated_duration_minutes: 30, planned_start_at: '2026-09-22T06:50:00Z', planned_end_at: '2026-09-22T07:20:00Z' }
          ]
        };
      }
      if (url === '/today/save') {
        planSaved = true;
        return { status: 'SUCCESS' };
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
      expect(api.post).toHaveBeenCalledWith('/today/preview', expect.any(Object));
      expect(screen.getByRole('button', { name: /^SAVE$/i })).toBeInTheDocument();
    });

    // Click Save inside MrBloom right panel
    const saveButton = screen.getByRole('button', { name: /^SAVE$/i });
    await fireEvent.click(saveButton);

    // Wait for the save post request to complete
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/today/save', expect.any(Object));
    });
    
    // Open/reload Today -> Verify the two persisted tasks
    const todayAfter = render(TodayPage);
    await waitFor(() => {
      expect(todayAfter.container.textContent).toMatch(/Today I need to read chapter 3 for/);
      expect(todayAfter.container.textContent).toMatch(/review flashcards for/);
    });
  });
});
