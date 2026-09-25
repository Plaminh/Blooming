import { render } from '@testing-library/svelte';
import { expect, test, vi } from 'vitest';
import type { Task } from '../../types';
import TodayTimeline from './TodayTimeline.svelte';

test('spaces every hour equally and positions unsorted tasks by their start time', () => {
  const tasks: Task[] = [
    {
      id: 'later', title: 'Later task', startTime: '11:30', endTime: '12:30',
      durationString: '(1 hour)', status: 'upcoming', category: 'Work', iconRef: 'document'
    },
    {
      id: 'earlier', title: 'Earlier task', startTime: '09:00', endTime: '10:00',
      durationString: '(1 hour)', status: 'in-progress', category: 'Learning', iconRef: 'book'
    }
  ];
  const { container, getByRole } = render(TodayTimeline, {
    tasks, currentDate: new Date(2024, 3, 23), selectedTaskId: 'earlier',
    onSelect: vi.fn(), onDateChange: vi.fn()
  });
  const top = (element: HTMLElement) => Number.parseFloat(element.style.top);
  const markers = [...container.querySelectorAll<HTMLElement>('.marker')];
  expect(markers).toHaveLength(10);
  const hourSpacing = top(markers[1]) - top(markers[0]);
  expect(hourSpacing).toBeGreaterThan(0);
  for (let index = 1; index < markers.length; index++) {
    expect(top(markers[index]) - top(markers[index - 1])).toBe(hourSpacing);
  }
  const earlier = getByRole('button', { name: /Earlier task/ });
  const later = getByRole('button', { name: /Later task/ });
  expect(top(later) - top(earlier)).toBe(hourSpacing * 2.5);
});

test('positions the current-time marker proportionally between hour ticks', () => {
  const { container, getByTestId } = render(TodayTimeline, {
    tasks: [], currentDate: new Date(2024, 3, 23), isToday: true, planTimezone: 'UTC',
    now: new Date('2024-04-23T15:30:00Z'), selectedTaskId: '',
    onSelect: vi.fn(), onDateChange: vi.fn()
  });
  const top = (element: HTMLElement) => Number.parseFloat(element.style.top);
  const at15 = container.querySelector<HTMLElement>('[data-hour="15:00"]')!;
  const at16 = container.querySelector<HTMLElement>('[data-hour="16:00"]')!;
  const marker = getByTestId('current-time-marker');
  const tickCenterOffset = 12;
  expect(top(marker)).toBeGreaterThan(top(at15) + tickCenterOffset);
  expect(top(marker)).toBeLessThan(top(at16) + tickCenterOffset);
  expect(marker).toHaveAttribute('aria-label', 'Current time 15:30');
  expect(top(marker)).not.toBe(top(container.querySelector<HTMLElement>('[data-hour="13:00"]')!) + tickCenterOffset);
});

test('expands the rail and positions work and breaks from timestamps', () => {
  const tasks: Task[] = [
    {
      id: 'work', title: 'Presentation', startTime: '16:45', endTime: '17:45',
      durationString: '(60 min)', status: 'upcoming', category: 'Work', iconRef: 'document'
    },
    {
      id: 'break', title: 'Break', startTime: '18:15', endTime: '18:20',
      durationString: '(5 min)', status: 'upcoming', category: null, iconRef: 'break'
    }
  ];
  const { container, getByTestId } = render(TodayTimeline, {
    tasks, currentDate: new Date(2024, 3, 23), isToday: false, selectedTaskId: 'work',
    onSelect: vi.fn(), onDateChange: vi.fn()
  });
  const top = (element: HTMLElement) => Number.parseFloat(element.style.top);
  expect(container.querySelector('.timeline-canvas')).toHaveAttribute('data-range', '09:00-19:00');
  expect(container.querySelector('[data-hour="19:00"]')).toBeInTheDocument();
  const work = getByTestId('timeline-task');
  const breakCard = getByTestId('timeline-break');
  const at16 = container.querySelector<HTMLElement>('[data-hour="16:00"]')!;
  const at17 = container.querySelector<HTMLElement>('[data-hour="17:00"]')!;
  expect(top(work)).toBeGreaterThan(top(at16) + 12);
  expect(top(work)).toBeLessThan(top(at17) + 12);
  expect(top(breakCard) - top(work)).toBeCloseTo(105, 5);
});

test('recreates identical geometry from reloaded saved timestamps', () => {
  const tasks: Task[] = [{
    id: 'saved', title: 'Saved task', startTime: '15:50', endTime: '16:40',
    durationString: '(50 min)', status: 'upcoming', category: 'Learning', iconRef: 'book'
  }];
  const props = {
    tasks, currentDate: new Date(2024, 3, 23), isToday: true, planTimezone: 'UTC',
    now: new Date('2024-04-23T15:30:00Z'), selectedTaskId: 'saved',
    onSelect: vi.fn(), onDateChange: vi.fn()
  };
  const first = render(TodayTimeline, props);
  const firstTop = first.getByTestId('timeline-task').style.top;
  const firstRange = first.container.querySelector('.timeline-canvas')?.getAttribute('data-range');
  first.unmount();

  const reloaded = render(TodayTimeline, props);
  expect(reloaded.getByTestId('timeline-task').style.top).toBe(firstTop);
  expect(reloaded.container.querySelector('.timeline-canvas')).toHaveAttribute('data-range', firstRange);
});
