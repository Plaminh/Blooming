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
          { id: 'm1', title: 'M1', targetDate: '2024-04-30', expectedOutcome: 'First result' }
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

  it('renders returned roadmap assumptions once and hides the section when empty', () => {
    mrBloomStore.update(state => ({
      ...state,
      assumptions: [
        { id: 'framework-1', kind: 'FRAMEWORK', text: "Generated using Blooming's default 3-step roadmap framework.", task_id: null },
        { id: 'framework-2', kind: 'FRAMEWORK', text: "Generated using Blooming's default 3-step roadmap framework.", task_id: null }
      ]
    }));
    const rendered = render(PlanDraftPreview);

    expect(rendered.getByRole('region', { name: 'Roadmap assumptions' })).toBeInTheDocument();
    expect(rendered.getAllByText("Generated using Blooming's default 3-step roadmap framework.")).toHaveLength(1);

    rendered.unmount();
    mrBloomStore.update(state => ({ ...state, assumptions: [] }));
    const empty = render(PlanDraftPreview);
    expect(empty.queryByRole('region', { name: 'Roadmap assumptions' })).toBeNull();
  });

  it('keeps the complete milestone title in an unconstrained editable field', () => {
    const fullTitle = 'Define the complete AI course project scope and submission requirements';
    mrBloomStore.update(state => ({
      ...state,
      activeDraft: state.activeDraft?.type === 'roadmap'
        ? { ...state.activeDraft, milestones: [{ id: 'm1', title: fullTitle, targetDate: '2024-04-30' }] }
        : state.activeDraft
    }));
    const { getByRole } = render(PlanDraftPreview);
    const title = getByRole('textbox', { name: 'Milestone title' }) as HTMLInputElement;

    expect(title.value).toBe(fullTitle);
    expect(title).not.toHaveAttribute('maxlength');
  });

  it('preserves add, remove, and discard roadmap actions', async () => {
    const { getByRole } = render(PlanDraftPreview);

    await fireEvent.click(getByRole('button', { name: 'ADD MILESTONE' }));
    let state: MrBloomState | undefined;
    mrBloomStore.subscribe(value => state = value)();
    expect(state?.activeDraft?.type === 'roadmap' && state.activeDraft.milestones.map(item => item.id)).toEqual(['m1', 'm2']);

    await fireEvent.click(getByRole('button', { name: 'Remove M1' }));
    mrBloomStore.subscribe(value => state = value)();
    expect(state?.activeDraft?.type === 'roadmap' && state.activeDraft.milestones.map(item => item.id)).toEqual(['m2']);

    await fireEvent.click(getByRole('button', { name: 'DISCARD' }));
    mrBloomStore.subscribe(value => state = value)();
    expect(state?.activeDraft).toBeNull();
  });
});
