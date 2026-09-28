import { api, getTodayPlan, completeTodayTask, replanToday, startFocusSession } from '$lib/api';
import type { TodayResponse } from '$lib/api/types';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, fireEvent, screen, waitFor } from '@testing-library/svelte';
import TodayPage from "../../../routes/(app)/today/+page.svelte";
import * as navigation from '$app/navigation';

vi.mock('$app/navigation', () => ({
  goto: vi.fn()
}));

vi.mock('$lib/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    put: vi.fn()
  }
}));

const mockBlocks = [
  {
    id: '1',
    task_id: '1',
    title: 'Study databases',
    planned_start_at: '2024-04-23T09:00:00Z',
    planned_end_at: '2024-04-23T10:00:00Z',
    status: 'ACTIVE',
    block_type: 'WORK'
  },
  {
    id: '3',
    task_id: '3',
    title: 'Finish proposal',
    planned_start_at: '2024-04-23T11:00:00Z',
    planned_end_at: '2024-04-23T12:00:00Z',
    status: 'PLANNED',
    block_type: 'WORK'
  }
];

describe('Today Screen Feature', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    window.history.replaceState({}, '', '/today');
    vi.useFakeTimers({ toFake: ['Date'] });
    vi.setSystemTime(new Date('2024-04-23T09:00:00Z'));
    HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
    HTMLDialogElement.prototype.close = function () {
      this.removeAttribute('open');
      this.dispatchEvent(new Event('close'));
    };

        vi.mocked(api.get).mockImplementation(async (url: string) => {
      if (url === '/me/settings') return { default_focus_minutes: 50, default_break_minutes: 10 };
      throw new Error(`Unexpected request: ${url}`);
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders the initial formatted displayed date correctly', async () => {
    render(TodayPage);
    expect(screen.getByText('Tue, Apr 23, 2024')).toBeInTheDocument();
  });

  it('handles date transitions (previous/next/today) and empty-day state', async () => {
    render(TodayPage);
    const prevBtn = screen.getByLabelText('Previous day');
    const nextBtn = screen.getByLabelText('Next day');
    const todayBtn = screen.getByText('Today');

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getAllByText('Study databases').length).toBeGreaterThan(0);
    });

    // Move to next day (Apr 24)
    await fireEvent.click(nextBtn);
    expect(screen.getByText('Wed, Apr 24, 2024')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Return to today' })).toHaveTextContent('Apr 24');
    
    // Day without mock tasks shows empty state
    await waitFor(() => {
      expect(screen.getAllByText('No tasks scheduled for this day.').length).toBeGreaterThan(0);
    });

    // Move to previous day (Apr 23)
    await fireEvent.click(prevBtn);
    expect(screen.getByText('Tue, Apr 23, 2024')).toBeInTheDocument();
    
    // Jump to Today (current system date, mocked to Apr 23)
    await fireEvent.click(todayBtn);
    expect(screen.getByRole('button', { name: 'Today' })).toBeInTheDocument();
    // Should show tasks because it's the demo day
    await waitFor(() => {
      expect(screen.getAllByText('Study databases').length).toBeGreaterThan(0);
    });
  });

  it('supports task selection and Task Details derivation', async () => {
    render(TodayPage);
    
    await waitFor(() => {
      expect(screen.getByText('Finish proposal')).toBeInTheDocument();
    });

    const taskButton = screen.getByText('Finish proposal');
    await fireEvent.click(taskButton);
    
    // The Task Details panel should update to show its category
    expect(screen.getByText('Uncategorized')).toBeInTheDocument(); // No category supplied by the API
  });

  it('supports single focus-preset selection and Start Focus local action', async () => {
    render(TodayPage);
    
    await waitFor(() => {
      expect(screen.getAllByText('Study databases').length).toBeGreaterThan(0);
    });
    
    // 25/5 is selected by default
    const preset50 = screen.getByText('50/10');
    await fireEvent.click(preset50);
    
    // The Start Focus button should be enabled because a task is selected by default (Task 1)
    const startFocusBtn = screen.getByText(/START FOCUS/);
    expect(startFocusBtn).not.toBeDisabled();
    
    await fireEvent.click(startFocusBtn);
    expect(startFocusSession).toHaveBeenCalledWith(expect.any(Object));
  });

  it('uses saved custom durations when starting focus', async () => {
    vi.mocked(api.put).mockResolvedValue({ default_focus_minutes: 45, default_break_minutes: 15 });
    render(TodayPage);
    await waitFor(() => expect(screen.getAllByText('Study databases').length).toBeGreaterThan(0));

    await fireEvent.click(screen.getByRole('button', { name: /CUSTOM/i }));
    await screen.findByRole('dialog', { name: 'CUSTOM FOCUS TIMER' });
    await fireEvent.change(screen.getByLabelText('Focus duration'), { target: { value: '45' } });
    await fireEvent.change(screen.getByLabelText('Break duration'), { target: { value: '15' } });
    await fireEvent.click(screen.getByRole('button', { name: 'Save' }));
    await waitFor(() => expect(api.put).toHaveBeenCalled());

    await fireEvent.click(screen.getByText('START FOCUS'));
    await waitFor(() => expect(api.post).toHaveBeenCalledWith('/focus/start', {
      task_id: '1',
      planned_focus_seconds: 45 * 60,
      planned_break_seconds: 15 * 60,
    }));
  });

  it('loads the saved target date supplied after replacement navigation', async () => {
    window.history.replaceState({}, '', '/today?date=2024-04-24');
    render(TodayPage);

    await waitFor(() => {
      expect(getTodayPlan).toHaveBeenCalledWith('2024-04-24');
    });
    expect(screen.getByText('Wed, Apr 24, 2024')).toBeInTheDocument();
  });

  it('renders insufficient-time partial schedules as warnings after load', async () => {
    vi.mocked(api.get).mockResolvedValue({
      plan_date: '2024-04-23', status: 'ACTIVE', timezone: 'UTC', blocks: mockBlocks,
      unscheduled_tasks: [{ draft_task_id: 'd3', title: 'Optional reading', reason: 'INSUFFICIENT_TIME' }],
      reasons: [{ code: 'INSUFFICIENT_TIME', task_id: 'd3' }], reality_check: null
    });

    render(TodayPage);

    const notice = await screen.findByRole('status');
    expect(notice).toHaveAttribute('data-severity', 'warning');
    expect(notice).toHaveTextContent(
      "1 task couldn't fit today. Your scheduled work was saved. Adjust your availability or replan."
    );
    expect(notice).not.toHaveTextContent('INSUFFICIENT_TIME');
    expect(notice).not.toHaveTextContent('d3');
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('keeps action and network failures at error severity', async () => {
    vi.mocked(api.post).mockRejectedValue(new Error('Network unavailable'));
    render(TodayPage);
    await waitFor(() => expect(screen.getAllByText('Study databases').length).toBeGreaterThan(0));

    await fireEvent.click(screen.getByText(/START FOCUS/));

    const notice = await screen.findByRole('alert');
    expect(notice).toHaveAttribute('data-severity', 'error');
    expect(notice).toHaveTextContent('Network unavailable');
  });

  it('marks task complete and updates status', async () => {
    vi.mocked(completeTodayTask).mockResolvedValue(undefined);
    render(TodayPage);
    await waitFor(() => expect(screen.getAllByText('Study databases').length).toBeGreaterThan(0));

    const markCompleteBtn = screen.getByTestId('mark-complete-btn');
    await fireEvent.click(markCompleteBtn);

    expect(api.patch).toHaveBeenCalledWith('/today/tasks/1/status', { status: 'COMPLETED' });
    await waitFor(() => {
      expect(screen.getByTestId('mark-complete-btn')).toBeDisabled();
      expect(screen.getByTestId('mark-complete-btn')).toHaveTextContent('COMPLETED');
    });
  });

  it('executes quick replan and refreshes schedule', async () => {
    vi.mocked(api.post).mockResolvedValue({
      plan_date: '2024-04-23',
      status: 'ACTIVE',
      timezone: 'UTC',
      blocks: [
        {
          id: '1',
          task_id: '1',
          title: 'Study databases (Replanned)',
          planned_start_at: '2024-04-23T09:30:00Z',
          planned_end_at: '2024-04-23T10:30:00Z',
          status: 'ACTIVE',
          block_type: 'WORK', description: null, category: null, importance: null, urgency: null, is_recurring: false
        }
      ],
      unscheduled_tasks: [], reasons: [], reality_check: null
    });

    render(TodayPage);
    await waitFor(() => expect(screen.getAllByText('Study databases').length).toBeGreaterThan(0));

    const quickReplanBtn = screen.getByTestId('quick-replan-btn');
    await fireEvent.click(quickReplanBtn);

    const todayStr = (new Date()).toLocaleDateString('en-CA');
    expect(replanToday).toHaveBeenCalledWith(todayStr);
    await waitFor(() => {
      expect(screen.getAllByText('Study databases (Replanned)').length).toBeGreaterThan(0);
    });
  });

  it('navigates to Mr. Bloom carrying date and taskId when Adjust is clicked', async () => {
    render(TodayPage);
    await waitFor(() => expect(screen.getAllByText('Study databases').length).toBeGreaterThan(0));

    // Right Rail Adjust button with taskId
    const adjustRailBtn = screen.getByTestId('rail-adjust-bloom-btn');
    await fireEvent.click(adjustRailBtn);
    expect(navigation.goto).toHaveBeenCalledWith('/mr-bloom?date=2024-04-23&taskId=1');

    // Bottom Actions Adjust button without taskId
    const adjustBottomBtn = screen.getByTestId('bottom-adjust-bloom-btn');
    await fireEvent.click(adjustBottomBtn);
    expect(navigation.goto).toHaveBeenCalledWith('/mr-bloom?date=2024-04-23');
  });
});
