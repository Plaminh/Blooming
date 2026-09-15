import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import StatisticsPage from '../../../routes/statistics/+page.svelte';

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

  it('bar chart renders 7 bars', () => {
    const { container } = render(StatisticsPage);
    const bars = container.querySelectorAll('.bar-chart-column');
    expect(bars.length).toBe(7);
  });

  it('plan history table displays 4 rows initially', () => {
    const { container } = render(StatisticsPage);
    const rows = container.querySelectorAll('.plan-history-row');
    expect(rows.length).toBe(4);
  });

  it('filter buttons toggle correctly', async () => {
    const { container } = render(StatisticsPage);
    const completedBtn = screen.getByRole('button', { name: 'Completed' });
    
    await fireEvent.click(completedBtn);
    
    // Only completed rows should be visible
    const rows = container.querySelectorAll('.plan-history-row');
    expect(rows.length).toBeGreaterThan(0);
    
    // Check if the badges in the rows say "Completed"
    const badges = container.querySelectorAll('.status-badge');
    badges.forEach(badge => {
      expect(badge.textContent?.trim()).toBe('Completed');
    });
  });

  it('pagination navigates between pages', async () => {
    const { container } = render(StatisticsPage);
    
    // Assuming mock data has 11 items, so 3 pages with 4 items each
    expect(container.querySelector('.page-indicator')?.textContent).toBe('1 / 3');
    
    const nextBtn = screen.getByLabelText('Next page');
    await fireEvent.click(nextBtn);
    
    expect(container.querySelector('.page-indicator')?.textContent).toBe('2 / 3');
  });
});
