import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/svelte';
import GoalDetailsPanel from './GoalDetailsPanel.svelte';

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

  it('allows inline editing of goal title and description', async () => {
    const { getByText, getByRole, getByPlaceholderText, queryByText } = render(GoalDetailsPanel, {
      goal: FIXTURE_GOAL,
      onUpdateMilestone: vi.fn()
    });

    expect(getByText('Launch MVP')).toBeInTheDocument();
    
    // Start editing
    const editBtn = getByRole('button', { name: 'Edit Goal' });
    expect(editBtn).toBeInTheDocument();
  });
});
