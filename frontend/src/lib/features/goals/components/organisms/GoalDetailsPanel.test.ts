import { describe, it, expect, vi } from 'vitest';
import { render, waitFor } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { goalsStore } from '../../stores/goalsStore';
import GoalDetailsPanel from './GoalDetailsPanel.svelte';

vi.mock('../../stores/goalsStore', () => ({
  goalsStore: {
    updateGoal: vi.fn()
  }
}));

import type { Goal } from '../../models';

const FIXTURE_GOAL: Goal = {
  id: 'g1',
  title: 'Launch MVP',
  description: 'Get the first version of the app in the hands of users.',
  target_date: '2024-06-30T00:00:00Z',
  iconRef: 'sprout',
  milestones: []
};

describe('GoalDetailsPanel', () => {
  it('does not render a + Milestone button', () => {
    const { queryByRole, queryByText } = render(GoalDetailsPanel, { 
      goal: FIXTURE_GOAL,
      onUpdateMilestone: vi.fn()
    });

    expect(queryByRole('button', { name: /\+ Milestone/i })).toBeNull();
    expect(queryByText('+ Milestone')).toBeNull();
  });

  it('awaits save mutation, disables during pending, and closes on success', async () => {
    const user = userEvent.setup();
    let resolveMutation: () => void;
    const savePromise = new Promise<void>(res => { resolveMutation = res; });
    goalsStore.updateGoal = vi.fn().mockReturnValue(savePromise);

    const { getByText, getByRole, getByPlaceholderText, queryByText } = render(GoalDetailsPanel, {
      goal: FIXTURE_GOAL
    });

    const editBtn = getByRole('button', { name: 'Edit Goal' });
    await user.click(editBtn);

    const titleInput = getByPlaceholderText('Goal Title');
    await user.clear(titleInput);
    await user.type(titleInput, 'Updated Goal Title');

    const saveBtn = getByRole('button', { name: 'Save' });
    await user.click(saveBtn);

    // Save disabled while pending
    expect(saveBtn).toBeDisabled();
    expect(goalsStore.updateGoal).toHaveBeenCalledWith('g1', { title: 'Updated Goal Title', description: FIXTURE_GOAL.description });
    
    // Editor stays open while pending
    expect(titleInput).toBeInTheDocument();

    resolveMutation!();
    
    // Wait for editor to close after success
    await waitFor(() => {
        expect(queryByText('Save')).toBeNull();
    });
  });

  it('keeps editor open and surfaces error on mutation failure', async () => {
    const user = userEvent.setup();
    goalsStore.updateGoal = vi.fn().mockRejectedValue(new Error('Backend error'));

    const { getByText, getByRole, getByPlaceholderText } = render(GoalDetailsPanel, {
      goal: FIXTURE_GOAL
    });

    const editBtn = getByRole('button', { name: 'Edit Goal' });
    await user.click(editBtn);

    const saveBtn = getByRole('button', { name: 'Save' });
    await user.click(saveBtn);

    // Wait for error to surface
    await waitFor(() => {
        expect(getByText('Backend error')).toBeInTheDocument();
    });

    // Editor stays open
    expect(getByPlaceholderText('Goal Title')).toBeInTheDocument();
    
    // Save becomes re-enabled
    expect(saveBtn).not.toBeDisabled();
  });
});
