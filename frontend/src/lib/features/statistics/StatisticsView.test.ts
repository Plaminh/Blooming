import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import StatisticsPage from '../../../routes/(app)/statistics/+page.svelte';

// Mock desktopWindowService for tests
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

// Mock api to return expected test data
vi.mock('$lib/api', () => ({
  api: {
    get: vi.fn().mockImplementation((url: string) => {
      if (url.includes('/statistics/summary')) {
        return Promise.resolve({
          study_time_hours: 12,
          study_time_minutes: 30,
          study_day_count: 5,
          completed_plan_count: 10,
          unfinished_plan_count: 2
        });
      }
      if (url.includes('/statistics/daily')) {
        return Promise.resolve([
          { day_label: 'Mon', hours: 2, date: '2026-06-01' },
          { day_label: 'Tue', hours: 1, date: '2026-06-02' },
          { day_label: 'Wed', hours: 3, date: '2026-06-03' },
          { day_label: 'Thu', hours: 0, date: '2026-06-04' },
          { day_label: 'Fri', hours: 4, date: '2026-06-05' },
          { day_label: 'Sat', hours: 2, date: '2026-06-06' },
          { day_label: 'Sun', hours: 0.5, date: '2026-06-07' }
        ]);
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

        return Promise.resolve({
          items: items,
          total_items: 11,
          total_pages: 3,
          current_page: page,
          items_per_page: 4
        });
      }
      return Promise.resolve({});
    })
  }
}));

describe('Statistics View', () => {
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

  it('calendar renders June 2026', () => {
    render(StatisticsPage);
    expect(screen.getByText('June 2026')).toBeInTheDocument();
  });

  it('month navigation changes month label', async () => {
    render(StatisticsPage);
    const prevBtn = screen.getByLabelText('Previous month');
    await fireEvent.click(prevBtn);
    expect(screen.getByText('May 2026')).toBeInTheDocument();
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
});
