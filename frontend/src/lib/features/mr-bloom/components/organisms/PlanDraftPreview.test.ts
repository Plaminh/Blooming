import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import PlanDraftPreview from './PlanDraftPreview.svelte';
import { mrBloomStore, type MrBloomState } from '../../stores/mrBloomStore';
import { saveRoadmap } from '$lib/api';
import * as navigation from '$app/navigation';

vi.mock('$app/navigation', () => ({
  goto: vi.fn()
}));

vi.mock('$lib/api', () => ({ saveRoadmap: vi.fn() }));

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
        targetDate: '2024-06-30',
        milestones: [
          { title: 'M1', targetDate: '2024-04-30' }
        ]
      }, preview: null, sessionId: null, degraded: null, suggestions: [], assumptions: [], needsReplace: false
    });
  });

  it('calls Goal persistence correctly and navigates to /goals on success', async () => {
    const saveRoadmapMock = vi.mocked(saveRoadmap).mockResolvedValue({ id: 'goal-123' });

    const { getByRole, queryByText } = render(PlanDraftPreview);
    
    await fireEvent.click(getByRole('button', { name: /SAVE TO GOALS/i }));
    
    await waitFor(() => {
      expect(saveRoadmapMock).toHaveBeenCalledWith(
        null, expect.objectContaining({ goalTitle: 'Test Goal' }), expect.any(String)
      );
    });

    expect(navigation.goto).toHaveBeenCalledWith('/goals');
    expect(queryByText(/Failed to save goal/i)).toBeNull();

    let state: MrBloomState | undefined;
    mrBloomStore.subscribe(s => state = s)();
    expect(state?.activeDraft).toBeNull();
  });

  it('preserves draft and shows error on failure', async () => {
    vi.mocked(saveRoadmap).mockRejectedValue(new Error('Backend error'));

    const { getByRole, findByText } = render(PlanDraftPreview);
    
    await fireEvent.click(getByRole('button', { name: /SAVE TO GOALS/i }));
    
    expect(await findByText('Backend error')).toBeInTheDocument();
    expect(navigation.goto).not.toHaveBeenCalled();
    
    let state: MrBloomState | undefined;
    mrBloomStore.subscribe(s => state = s)();
    expect(state?.activeDraft).not.toBeNull();
  });
});
