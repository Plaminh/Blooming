import { expect, test } from 'vitest';
import { fireEvent, render, screen, within } from '@testing-library/svelte';
import DraftTaskSummary from './DraftTaskSummary.svelte';

const task = {
  id: 'task-1', title: 'Read documentation with a deliberately long descriptive title', durationMin: 45,
  priority: 'MEDIUM' as const, importance: 'CORE' as const, category: null,
  estimateSource: 'USER' as const, breakAfterMin: null, deadline: null,
  schedulingType: 'FLEXIBLE' as const, fixedStart: null, fixedEnd: null,
  dependencies: [], splittable: false
};

test('groups primary controls in the main row and collapses unused time actions', () => {
  const { container } = render(DraftTaskSummary, { task });
  const mainRow = container.querySelector('.main-row');
  const constraints = container.querySelector('.constraint-editor');
  const disclosure = screen.getByText('Add time constraint').closest('details');

  expect(mainRow).not.toBeNull();
  expect(constraints).not.toBeNull();
  expect(within(mainRow as HTMLElement).getByDisplayValue(task.title)).toBeInTheDocument();
  expect(within(mainRow as HTMLElement).getByDisplayValue('45')).toBeInTheDocument();
  expect(within(mainRow as HTMLElement).getByRole('combobox')).toHaveValue('CORE');
  expect(within(mainRow as HTMLElement).getByRole('button', { name: `Remove ${task.title}` })).toBeInTheDocument();
  expect(mainRow?.contains(constraints)).toBe(false);
  expect(disclosure).not.toHaveAttribute('open');
});

test('shows server fixed times as clock values and marks repeating or carried work', () => {
  render(DraftTaskSummary, {
    task: {
      ...task,
      schedulingType: 'FIXED' as const,
      fixedStart: '2026-09-28T19:00:00+07:00',
      fixedEnd: '2026-09-28T20:00:00+07:00',
      recurrence: { freq: 'WEEKLY' as const, weekdays: [0, 2] },
      sourceTaskId: '6a4f6c1e-0000-4000-8000-000000000001'
    }
  });

  expect(screen.getByLabelText('Start time')).toHaveValue('19:00');
  expect(screen.getByLabelText('End time')).toHaveValue('20:00');
  expect(screen.getByText('↻ Repeats weekly · Mon, Wed')).toBeInTheDocument();
  expect(screen.getByText('Carried over')).toBeInTheDocument();
});

test('keeps sequential title characters editable while the field is focused', async () => {
  render(DraftTaskSummary, { task: { ...task, title: 'Study algorithms' } });
  const input = screen.getByRole('textbox', { name: 'Title' });

  await fireEvent.focus(input);
  await fireEvent.input(input, { target: { value: 'Review' } });
  await fireEvent.input(input, { target: { value: 'Review algorithms' } });

  expect(input).toHaveValue('Review algorithms');
});
