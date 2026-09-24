import { expect, test } from 'vitest';
import { render, screen, within } from '@testing-library/svelte';
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
