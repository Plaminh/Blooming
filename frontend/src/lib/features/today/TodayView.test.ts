import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, fireEvent, screen, waitFor } from '@testing-library/svelte';
import TodayPage from "../../../routes/(app)/today/+page.svelte";
import { api } from '$lib/api';

vi.mock('$lib/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn()
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
    vi.useFakeTimers({ toFake: ['Date'] });
    vi.setSystemTime(new Date('2024-04-23T09:00:00Z'));

    (api.get as any).mockImplementation(async (url: string) => {
      const parsedUrl = new URL(url, "http://localhost");
      if (parsedUrl.pathname === '/today') {
        const dateParam = parsedUrl.searchParams.get('date');
        if (!dateParam || dateParam === '2024-04-23') {
          return { blocks: mockBlocks };
        }
      }
      return { blocks: [] };
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
    
    // Day without mock tasks shows empty state
    await waitFor(() => {
      expect(screen.getAllByText('No tasks scheduled for this day.').length).toBeGreaterThan(0);
    });

    // Move to previous day (Apr 23)
    await fireEvent.click(prevBtn);
    expect(screen.getByText('Tue, Apr 23, 2024')).toBeInTheDocument();
    
    // Jump to Today (current system date, mocked to Apr 23)
    await fireEvent.click(todayBtn);
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
    expect(api.post).toHaveBeenCalledWith('/focus/start', expect.any(Object));
  });
});
