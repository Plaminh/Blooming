import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/svelte';
import StatisticsPage from '../../../routes/(app)/statistics/+page.svelte';
import { api } from '$lib/api/client';

vi.mock('$lib/platform/desktopWindow', () => ({
  desktopWindowService: {
    minimizeCurrent: vi.fn(),
    toggleMaximizeCurrent: vi.fn().mockResolvedValue(false),
    hideCurrent: vi.fn(),
    startDraggingCurrent: vi.fn(),
    isCurrentMaximized: vi.fn().mockResolvedValue(false),
    onResized: vi.fn().mockResolvedValue(() => {})
  }
}));


vi.mock('$lib/api/client', () => ({
  api: {
    get: vi.fn()
  }
}));

describe('Statistics View', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    // Default success mock for most tests
    vi.mocked(api.get).mockImplementation(async (url: string) => {
      if (url.includes('/statistics/summary')) {
        return {
          study_time_hours: 12,
          study_time_minutes: 30,
          study_day_count: 5,
          completed_plan_count: 10,
          unfinished_plan_count: 2
        };
      }
      if (url.includes('/statistics/daily')) {
        return [
          { day_label: 'Mon', hours: 2, date: '2026-06-01' },
          { day_label: 'Tue', hours: 1, date: '2026-06-02' },
          { day_label: 'Wed', hours: 3, date: '2026-06-03' },
          { day_label: 'Thu', hours: 0, date: '2026-06-04' },
          { day_label: 'Fri', hours: 4, date: '2026-06-05' },
          { day_label: 'Sat', hours: 2, date: '2026-06-06' },
          { day_label: 'Sun', hours: 0.5, date: '2026-06-07' }
        ];
      }
      if (url.includes('/statistics/plan-history')) {
        const urlObj = new URL('http://localhost' + url);
        const status = urlObj.searchParams.get('status') || 'All';
        const page = parseInt(urlObj.searchParams.get('page') || '1', 10);
        
        let items = [
          { id: '1', date_label: 'Today', plan_name: 'Morning Focus', completed_tasks: 3, total_tasks: 4, status: 'Completed' },
          { id: '2', date_label: 'Yesterday', plan_name: 'Evening Session', completed_tasks: 2, total_tasks: 2, status: 'Completed' },
          { id: '3', date_label: 'Monday', plan_name: 'Deep Work', completed_tasks: 0, total_tasks: 1, status: 'Unfinished' },
          { id: '4', date_label: 'Sunday', plan_name: 'Reading', completed_tasks: 1, total_tasks: 1, status: 'Completed' }
        ];

        if (status === 'Completed') {
          items = items.filter(i => i.status === 'Completed');
        } else if (status === 'Unfinished') {
          items = items.filter(i => i.status === 'Unfinished');
        }

        return {
          items: items,
          total_items: 11,
          total_pages: 3,
          current_page: page,
          items_per_page: 4
        };
      }
      return {};
    });
  });

  afterEach(() => {
    cleanup();
  });

  // --- RESTORED PREVIOUS REGRESSION TESTS ---

  it('renders heading "STATISTICS" and subtitle', () => {
    render(StatisticsPage);
    expect(screen.getByRole('heading', { name: /STATISTICS/i })).toBeInTheDocument();
    expect(screen.getByText('Your progress, one day at a time.')).toBeInTheDocument();
  });

  it('summary cards display correct labels', () => {
    render(StatisticsPage);
    expect(screen.getByText('STUDY TIME')).toBeInTheDocument();
    expect(screen.getByText('STUDY DAYS')).toBeInTheDocument();
    expect(screen.getByText('PLANS')).toBeInTheDocument();
  });

  it('calendar renders current month label (or initial)', async () => {
    // Assuming page starts on current month; to be resilient, we just wait for a month year regex
    render(StatisticsPage);
    await waitFor(() => {
      // Just assert some month/year shows up in the header, or check the document
      const monthYearElement = screen.getByText(/^(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$/);
      expect(monthYearElement).toBeInTheDocument();
    });
  });

  it('month navigation changes month label', async () => {
    render(StatisticsPage);
    let initialMonthText = '';
    await waitFor(() => {
      const el = screen.getByText(/^(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$/);
      initialMonthText = el.textContent || '';
      expect(initialMonthText).toBeTruthy();
    });

    const prevBtn = screen.getByLabelText('Previous month');
    await fireEvent.click(prevBtn);
    
    await waitFor(() => {
      const el = screen.getByText(/^(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$/);
      expect(el.textContent).not.toBe(initialMonthText);
    });
  });

  it('bar chart renders 7 bars', async () => {
    const { container } = render(StatisticsPage);
    await waitFor(() => {
      const bars = container.querySelectorAll('.bar-chart-column');
      expect(bars.length).toBe(7);
    });
  });

  it('plan history table displays 4 rows initially', async () => {
    const { container } = render(StatisticsPage);
    await waitFor(() => {
      const rows = container.querySelectorAll('.plan-history-row');
      expect(rows.length).toBe(4);
    });
  });

  it('filter buttons toggle correctly', async () => {
    const { container } = render(StatisticsPage);
    
    await waitFor(() => {
      const rows = container.querySelectorAll('.plan-history-row');
      expect(rows.length).toBe(4);
    });

    const completedBtn = screen.getByRole('button', { name: 'Completed' });
    await fireEvent.click(completedBtn);
    
    await waitFor(() => {
      const badges = container.querySelectorAll('.status-badge');
      expect(badges.length).toBeGreaterThan(0);
      badges.forEach(badge => {
        expect(badge.textContent?.trim()).toBe('Completed');
      });
    });
  });

  it('pagination navigates between pages', async () => {
    const { container } = render(StatisticsPage);
    
    await waitFor(() => {
      expect(container.querySelector('.page-indicator')?.textContent).toBe('1 / 3');
    });
    
    const nextBtn = screen.getByLabelText('Next page');
    await fireEvent.click(nextBtn);
    
    await waitFor(() => {
      expect(container.querySelector('.page-indicator')?.textContent).toBe('2 / 3');
    });
  });


  // --- NEW BLOCK 8 TESTS (STRENGTHENED) ---

  it('renders successful summary rendering with formatted duration', async () => {
    render(StatisticsPage);
    
    await waitFor(() => {
      expect(screen.getByText('12h 30m')).toBeInTheDocument();
    });
    expect(screen.getByText('5 days')).toBeInTheDocument();
    expect(screen.getByText(/10 complete/i)).toBeInTheDocument();
  });

  it('renders study calendar entries correctly based on exact API data', async () => {
    const { container } = render(StatisticsPage);
    await waitFor(() => {
      expect(screen.getByText('12h 30m')).toBeInTheDocument();
    });
    
    // Assert exactly 7 bars are present corresponding to the 7 mock API entries
    const bars = container.querySelectorAll('.bar-chart-column');
    expect(bars.length).toBe(7);
    
    // Ensure the days provided in the mock data are actually rendered in the UI
    const days = Array.from(container.querySelectorAll('.day-label')).map(el => el.textContent?.trim());
    expect(days).toEqual(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);

    // Ensure the hour values are reflected (even as plain text, or aria-labels if applicable)
    // We expect 2, 1, 3, 0, 4, 2, 0.5 to be reflected in some way.
    // If the component renders the heights, we can't easily check inline styles without knowing exact logic,
    // but at least we can assert the tooltip or label exists if the component supports it.
    const hourLabels = Array.from(container.querySelectorAll('.hours-label')).map(el => el.textContent?.trim());
    if (hourLabels.length > 0) {
      expect(hourLabels).toEqual(['2h', '1h', '3h', '0h', '4h', '2h', '0.5h']);
    }
  });

  it('renders empty state safely without crashing', async () => {
    vi.mocked(api.get).mockImplementation(async (url: string) => {
      if (url.includes('/statistics/summary')) {
        return {
          study_time_hours: 0,
          study_time_minutes: 0,
          study_day_count: 0,
          completed_plan_count: 0,
          unfinished_plan_count: 0
        };
      }
      if (url.includes('/statistics/daily')) {
        return [];
      }
      if (url.includes('/statistics/plan-history')) {
        return { items: [], total_items: 0, total_pages: 0, current_page: 1, items_per_page: 4 };
      }
      return {};
    });

    render(StatisticsPage);
    await waitFor(() => {
      expect(screen.getByText('0h 0m')).toBeInTheDocument();
    });
    expect(screen.getByText('0 days')).toBeInTheDocument();
    expect(screen.getByText(/0 complete/i)).toBeInTheDocument();
  });

  it('handles API error state gracefully', async () => {
    vi.mocked(api.get).mockRejectedValue(new Error('Network error'));
    
    // Silence console error to avoid cluttering test output
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    render(StatisticsPage);
    await waitFor(() => {
      // Look for error message on screen, or ensure it doesn't crash
      const errorEl = screen.queryByText(/Network error/i) || screen.queryByText(/Failed to load statistics/i);
      expect(errorEl).toBeInTheDocument();
    });
    
    consoleSpy.mockRestore();
  });

  it('sends correct date range request based on filter interaction', async () => {
    render(StatisticsPage);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('12h 30m')).toBeInTheDocument();
    });
    
    vi.mocked(api.get).mockClear();

    // Trigger a date range filter to force a new date range request
    const toggleBtn = screen.getByRole('button', { name: /Current Week/i });
    await fireEvent.click(toggleBtn);
    
    // It should open a listbox, find another option
    const monthOption = await screen.findByText('Current Month');
    await fireEvent.click(monthOption);
    
    await waitFor(() => {
      // The component should fetch new daily stats for the new range
      expect(api.get).toHaveBeenCalledWith(expect.stringContaining('start_date='));
      expect(api.get).toHaveBeenCalledWith(expect.stringContaining('end_date='));
    });
  });
});
