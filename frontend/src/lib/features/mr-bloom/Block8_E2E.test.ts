import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, fireEvent, screen, waitFor } from '@testing-library/svelte';
import PlanningWorkspace from './components/organisms/PlanningWorkspace.svelte';
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

describe('Block 8 E2E: Task Splitting and Durations', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.useFakeTimers({ toFake: ['Date'] });
    vi.setSystemTime(new Date('2026-09-22T09:00:00Z'));
    HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
    HTMLDialogElement.prototype.close = function () {
      this.removeAttribute('open');
      this.dispatchEvent(new Event('close'));
    };

    (api.get as any).mockImplementation(async (url: string) => {
      if (url === '/me/settings') return { default_focus_minutes: 50, default_break_minutes: 10 };
      throw new Error(`Unexpected GET: ${url}`);
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const cases = [
    {
      name: 'Comma-separated tasks',
      input: 'Read for 30 min, write notes for 45 min',
      mockDraft: {
        tasks: [
          { id: 't1', title: 'Read for', durationMin: 30 },
          { id: 't2', title: 'write notes for', durationMin: 45 }
        ]
      }
    },
    {
      name: 'Semicolon-separated tasks',
      input: 'Read for 30 min; write notes for 45 min',
      mockDraft: {
        tasks: [
          { id: 't1', title: 'Read for', durationMin: 30 },
          { id: 't2', title: 'write notes for', durationMin: 45 }
        ]
      }
    },
    {
      name: 'Newline-separated tasks',
      input: 'Read for 30 min\nWrite notes for 45 min',
      mockDraft: {
        tasks: [
          { id: 't1', title: 'Read for', durationMin: 30 },
          { id: 't2', title: 'Write notes for', durationMin: 45 }
        ]
      }
    },
    {
      name: 'Numbered list',
      input: '1. Read for 30 min\n2. Write notes for 45 min',
      mockDraft: {
        tasks: [
          { id: 't1', title: 'Read for', durationMin: 30 },
          { id: 't2', title: 'Write notes for', durationMin: 45 }
        ]
      }
    },
    {
      name: 'Bulleted list',
      input: '- Read for 30 min\n- Write notes for 45 min',
      mockDraft: {
        tasks: [
          { id: 't1', title: 'Read for', durationMin: 30 },
          { id: 't2', title: 'Write notes for', durationMin: 45 }
        ]
      }
    },
    {
      name: 'Duration format: 1h',
      input: 'Study for 1h',
      mockDraft: {
        tasks: [{ id: 't1', title: 'Study for', durationMin: 60 }]
      }
    },
    {
      name: 'Duration format: 90p',
      input: 'Study for 90p',
      mockDraft: {
        tasks: [{ id: 't1', title: 'Study for', durationMin: 90 }]
      }
    },
    {
      name: 'Duration format: 45 min',
      input: 'Study for 45 min',
      mockDraft: {
        tasks: [{ id: 't1', title: 'Study for', durationMin: 45 }]
      }
    },
    {
      name: 'Duration format: 1h30',
      input: 'Study for 1h30',
      mockDraft: {
        tasks: [{ id: 't1', title: 'Study for', durationMin: 90 }]
      }
    },
    {
      name: 'Duration format: one-and-a-half hours',
      input: 'Study for one-and-a-half hours',
      mockDraft: {
        tasks: [{ id: 't1', title: 'Study for', durationMin: 90 }]
      }
    },
    {
      name: 'Duration format: Decimal hours',
      input: 'Study for 1.5h',
      mockDraft: {
        tasks: [{ id: 't1', title: 'Study for', durationMin: 90 }]
      }
    }
  ];

  cases.forEach(({ name, input, mockDraft }) => {
    it(`renders correct task count, titles, and durations for: ${name}`, async () => {
      (api.post as any).mockImplementation(async (url: string) => {
        if (url === '/assistant/chat') {
          return {
            reply: 'Draft ready.',
            session_id: 's1',
            intent: 'PLAN_DAY',
            tier: 'PARSER',
            draft: {
              type: 'today',
              planDate: '2026-09-22',
              timezone: 'UTC',
              windows: [{ start: '06:00', end: '22:00' }],
              tasks: mockDraft.tasks
            },
            preview: null,
            suggestions: []
          };
        }
        throw new Error(`Unexpected POST: ${url}`);
      });

      const bloom = render(PlanningWorkspace);
      const chatInput = screen.getByPlaceholderText(/Choose what you want to plan first/i);
      
      await fireEvent.input(chatInput, { target: { value: input } });
      const sendButton = screen.getByRole('button', { name: 'Send' });
      await fireEvent.click(sendButton);

      await waitFor(() => {
        // Assert correct number of tasks rendered
        mockDraft.tasks.forEach(task => {
          expect(screen.getByDisplayValue(task.title)).toBeInTheDocument();
          const durationInputs = screen.getAllByDisplayValue(task.durationMin.toString());
          expect(durationInputs.length).toBeGreaterThan(0);
        });

        // Save should not be available before preview
        expect(screen.queryByRole('button', { name: /^SAVE$/i })).not.toBeInTheDocument();
      });

      bloom.unmount();
    });
  });

  it('multiple parsed tasks complete the explicit preview and save flow', async () => {
    const tasks = [
      { id: 't1', title: 'Read', durationMin: 30 },
      { id: 't2', title: 'Write notes', durationMin: 45 }
    ];
    (api.post as any).mockImplementation(async (url: string, payload: any) => {
      if (url === '/assistant/chat') return {
        reply: 'Draft ready.', session_id: 'block-8-session',
        draft: { type: 'today', planDate: '2026-09-22', timezone: 'UTC', windows: [{ start: '09:00', end: '12:00' }], tasks },
        preview: null, suggestions: []
      };
      if (url === '/today/preview') return {
        preview_token: 'block-8-preview', timezone: 'UTC', status: 'DRAFT', unscheduled_tasks: [], reasons: [], reality_check: null,
        blocks: payload.draft.tasks.map((task: any, index: number) => ({
          id: `b${index}`, draft_task_id: task.id, title: task.title, block_type: 'TASK',
          planned_start_at: `2026-09-22T${String(9 + index).padStart(2, '0')}:00:00Z`,
          planned_end_at: `2026-09-22T${String(9 + index).padStart(2, '0')}:30:00Z`
        }))
      };
      if (url === '/today/save') return { status: 'ACTIVE', blocks: [] };
      throw new Error(`Unexpected POST: ${url}`);
    });

    render(PlanningWorkspace);
    await fireEvent.input(screen.getByPlaceholderText(/Choose what you want to plan first/i), { target: { value: 'Read for 30 min, write notes for 45 min' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Send' }));
    await waitFor(() => expect(screen.getByDisplayValue('Write notes')).toBeInTheDocument());
    await fireEvent.click(screen.getByRole('button', { name: /GENERATE TIMELINE/i }));
    await waitFor(() => expect(screen.getByRole('button', { name: /^SAVE$/i })).toBeInTheDocument());
    expect(api.post).toHaveBeenCalledWith('/today/preview', expect.objectContaining({ draft: expect.objectContaining({ tasks }) }));
    await fireEvent.click(screen.getByRole('button', { name: /^SAVE$/i }));
    await waitFor(() => expect(api.post).toHaveBeenCalledWith('/today/save', expect.objectContaining({
      session_id: 'block-8-session', preview_token: 'block-8-preview', draft: expect.objectContaining({ tasks })
    })));
  });
});
