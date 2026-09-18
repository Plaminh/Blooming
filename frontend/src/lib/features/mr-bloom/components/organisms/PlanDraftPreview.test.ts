import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import PlanDraftPreview from './PlanDraftPreview.svelte';
import { mrBloomStore, type MrBloomState } from '../../stores/mrBloomStore';
import { goalsStore } from '$lib/features/goals/stores/goalsStore';
import * as navigation from '$app/navigation';

vi.mock('$app/navigation', () => ({
  goto: vi.fn()
}));

vi.mock('$lib/features/goals/stores/goalsStore', () => ({
  goalsStore: {
    createGoal: vi.fn(),
    addMilestone: vi.fn(),
    subscribe: vi.fn((cb) => { cb({ goals: [] }); return () => {}; })
  }
}));

describe('PlanDraftPreview save to goals', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mrBloomStore.set({
      chatHistory: [],
      isWaitingForResponse: false,
      previewMode: 'roadmap',
      activeDraft: {
        type: 'roadmap',
        goalTitle: 'Test Goal',
        goalDescription: 'Test Desc',
        targetDate: 'Jun 30, 2024',
        milestones: [
          { id: 'm1', title: 'M1', targetDate: 'Apr 30, 2024' }
        ]
      }
    });
  });

  it('calls Goal persistence correctly and navigates to /goals on success', async () => {
    const createGoalMock = vi.mocked(goalsStore.createGoal).mockResolvedValue({ id: 'goal-123' });
    const addMilestoneMock = vi.mocked(goalsStore.addMilestone).mockResolvedValue(undefined);

    const { getByRole, queryByText } = render(PlanDraftPreview);
    
    await fireEvent.click(getByRole('button', { name: /SAVE TO GOALS/i }));
    
    await waitFor(() => {
      expect(createGoalMock).toHaveBeenCalledWith({
        title: 'Test Goal',
        description: 'Test Desc',
        target_date: '2024-06-30'
      });
    });

    expect(addMilestoneMock).toHaveBeenCalledWith('goal-123', {
      title: 'M1',
      due_at: expect.any(String)
    });

    expect(navigation.goto).toHaveBeenCalledWith('/goals');
    expect(queryByText(/Failed to save goal/i)).toBeNull();

    let state: MrBloomState | undefined;
    mrBloomStore.subscribe(s => state = s)();
    expect(state?.activeDraft).toBeNull();
  });

  it('preserves draft and shows error on failure', async () => {
    vi.mocked(goalsStore.createGoal).mockRejectedValue(new Error('Backend error'));

    const { getByRole, findByText } = render(PlanDraftPreview);
    
    await fireEvent.click(getByRole('button', { name: /SAVE TO GOALS/i }));
    
    expect(await findByText('Backend error')).toBeInTheDocument();
    expect(navigation.goto).not.toHaveBeenCalled();
    
    let state: MrBloomState | undefined;
    mrBloomStore.subscribe(s => state = s)();
    expect(state?.activeDraft).not.toBeNull();
  });
});
