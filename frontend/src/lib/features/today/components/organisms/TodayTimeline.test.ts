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
  expect(markers).toHaveLength(8);
  const hourSpacing = top(markers[1]) - top(markers[0]);
  expect(hourSpacing).toBeGreaterThan(0);
  for (let index = 1; index < markers.length; index++) {
    expect(top(markers[index]) - top(markers[index - 1])).toBe(hourSpacing);
  }
  const earlier = getByRole('button', { name: /Earlier task/ });
  const later = getByRole('button', { name: /Later task/ });
  expect(top(later) - top(earlier)).toBe(hourSpacing * 2.5);
});
