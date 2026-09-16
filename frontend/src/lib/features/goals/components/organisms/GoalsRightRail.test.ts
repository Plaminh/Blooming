import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import GoalsRightRail from './GoalsRightRail.svelte';
import { FIXTURE_GOALS } from '../../models';

describe('GoalsRightRail', () => {
  it('renders safely with no selected goal or available actions', () => {
    const { container, queryByRole } = render(GoalsRightRail, { goal: null, onEdit: vi.fn(), onRefine: vi.fn() });
    expect(container.querySelector('.right-rail')).toBeInTheDocument();
    expect(queryByRole('button')).toBeNull();
    expect(queryByRole('heading', { name: 'NEXT MILESTONE' })).toBeNull();
  });

  it('renders the selected goal milestone and overall progress sections', () => {
    const { getByRole, getByText } = render(GoalsRightRail, { goal: FIXTURE_GOALS[0], onEdit: vi.fn(), onRefine: vi.fn() });
    expect(getByRole('heading', { name: 'NEXT MILESTONE' })).toBeInTheDocument();
    expect(getByRole('heading', { name: 'Build planning core' })).toBeInTheDocument();
    expect(getByRole('heading', { name: 'OVERALL PROGRESS' })).toBeInTheDocument();
    expect(getByText('2 / 4 milestones')).toBeInTheDocument();
    expect(getByText('50%')).toBeInTheDocument();
  });

  it('wires the edit and refine controls to their respective callbacks', async () => {
    const onEdit = vi.fn();
    const onRefine = vi.fn();
    const { getByRole } = render(GoalsRightRail, { goal: FIXTURE_GOALS[0], onEdit, onRefine });
    await fireEvent.click(getByRole('button', { name: 'EDIT MANUALLY' }));
    expect(onEdit).toHaveBeenCalledOnce();
    expect(onRefine).not.toHaveBeenCalled();
    await fireEvent.click(getByRole('button', { name: 'REFINE WITH MR. BLOOM' }));
    expect(onRefine).toHaveBeenCalledOnce();
    expect(onEdit).toHaveBeenCalledOnce();
  });

  it.each([null, FIXTURE_GOALS[0]])('does not render a local Garden panel (goal: %s)', (goal) => {
    const { container, queryByRole } = render(GoalsRightRail, { goal, onEdit: vi.fn(), onRefine: vi.fn() });
    expect(container.querySelector('.garden')).toBeNull();
    expect(queryByRole('link', { name: 'YOUR GARDEN' })).toBeNull();
    expect(queryByRole('heading', { name: 'YOUR GARDEN' })).toBeNull();
  });
});
