import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import GoalsRightRail from './GoalsRightRail.svelte';
import type { Goal } from '../../models';

const FIXTURE_GOALS: Goal[] = [
  {
    id: 'g1',
    title: 'Launch MVP',
    description: 'Get the first version of the app in the hands of users.',
    roadmap_summary: null,
    target_date: '2024-06-30T00:00:00Z',
    status: 'DRAFT',
    iconRef: 'sprout',
    milestones: [
      { id: 'm1', title: 'Design concept', description: 'Define core problem.', expected_outcome: null, target_date: null, status: 'COMPLETED', due_at: null },
      { id: 'm2', title: 'Build planning core', description: 'Build Today, Goals and Settings.', expected_outcome: null, target_date: null, status: 'IN_PROGRESS', due_at: null },
      { id: 'm3', title: 'Implement desktop widget', description: 'Create widget.', expected_outcome: null, target_date: null, status: 'PENDING', due_at: null },
      { id: 'm4', title: 'Validate MVP', description: 'Test with early users.', expected_outcome: null, target_date: null, status: 'PENDING', due_at: null }
    ]
  }
];

describe('GoalsRightRail', () => {
  it('renders safely with no selected goal or available actions', () => {
    const { container, queryByRole } = render(GoalsRightRail, { goal: null, onRefine: vi.fn() });
    expect(container.querySelector('.right-rail')).toBeInTheDocument();
    expect(queryByRole('button')).toBeNull();
    expect(queryByRole('heading', { name: 'NEXT MILESTONE' })).toBeNull();
  });

  it('renders the selected goal milestone and overall progress sections', () => {
    const { getByRole, getByText } = render(GoalsRightRail, { goal: FIXTURE_GOALS[0], onRefine: vi.fn() });
    expect(getByRole('heading', { name: 'NEXT MILESTONE' })).toBeInTheDocument();
    expect(getByRole('heading', { name: 'Build planning core' })).toBeInTheDocument();
    expect(getByRole('heading', { name: 'OVERALL PROGRESS' })).toBeInTheDocument();
    expect(getByText('1 / 4 milestones')).toBeInTheDocument();
    expect(getByText('25%')).toBeInTheDocument();
  });

  it('wires the adjust controls to their respective callbacks', async () => {
    const onRefine = vi.fn();
    const { getByRole, queryByRole } = render(GoalsRightRail, { goal: FIXTURE_GOALS[0], onRefine });
    expect(queryByRole('button', { name: 'EDIT MANUALLY' })).toBeNull();
    await fireEvent.click(getByRole('button', { name: 'ADJUST WITH MR. BLOOM' }));
    expect(onRefine).toHaveBeenCalledOnce();
  });

  it.each([null, FIXTURE_GOALS[0]])('does not render a local Garden panel (goal: %s)', (goal) => {
    const { container, queryByRole } = render(GoalsRightRail, { goal, onRefine: vi.fn() });
    expect(container.querySelector('.garden')).toBeNull();
    expect(queryByRole('link', { name: 'YOUR GARDEN' })).toBeNull();
    expect(queryByRole('heading', { name: 'YOUR GARDEN' })).toBeNull();
  });
});
