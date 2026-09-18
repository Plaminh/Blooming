import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import GoalsPage from './+page.svelte';
import { goalsStore } from '$lib/features/goals/stores/goalsStore';
import * as navigation from '$app/navigation';
import { overlayStore } from '$lib/shared/stores/overlayStore';

vi.mock('$app/navigation', () => ({
  goto: vi.fn()
}));

vi.mock('$lib/features/goals/stores/goalsStore', () => ({
  goalsStore: {
    loadGoals: vi.fn().mockResolvedValue([]),
    loadDueReminders: vi.fn().mockResolvedValue([]),
    createGoal: vi.fn(),
    addMilestone: vi.fn(),
    updateGoal: vi.fn(),
    updateMilestone: vi.fn(),
    subscribe: vi.fn((cb) => { cb({ goals: [], dueReminders: [], loading: false, error: null }); return () => {}; })
  }
}));

describe('Goals Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('navigates to /mr-bloom when CREATE GOAL WITH MR. BLOOM is clicked', async () => {
    // Override window.prompt just to ensure it's not called
    const promptSpy = vi.spyOn(window, 'prompt').mockImplementation(() => 'test');
    
    const { getByRole } = render(GoalsPage);
    
    const createBtn = getByRole('button', { name: /CREATE GOAL WITH MR\. BLOOM/i });
    await fireEvent.click(createBtn);
    
    expect(navigation.goto).toHaveBeenCalledWith('/mr-bloom');
    expect(promptSpy).not.toHaveBeenCalled();
    expect(goalsStore.createGoal).not.toHaveBeenCalled();
    
    promptSpy.mockRestore();
  });
});
