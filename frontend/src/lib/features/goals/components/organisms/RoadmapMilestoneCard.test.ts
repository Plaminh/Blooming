import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import RoadmapMilestoneCard from './RoadmapMilestoneCard.svelte';
import type { Milestone } from '../../models';

const FIXTURE_MILESTONE: Milestone = {
  id: 'm1',
  title: 'Design concept',
  description: null,
  expected_outcome: 'Define core problem.',
  status: 'PENDING',
  target_date: null,
  due_at: '2024-06-30T00:00:00Z',
};

describe('RoadmapMilestoneCard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders milestone data', () => {
    const { getByText } = render(RoadmapMilestoneCard, { milestone: FIXTURE_MILESTONE });
    expect(getByText('Design concept')).toBeInTheDocument();
    expect(getByText('Define core problem.')).toBeInTheDocument();
  });

  it('allows marking milestone as complete', async () => {
    const onUpdateMilestone = vi.fn();
    const { getByRole } = render(RoadmapMilestoneCard, { milestone: FIXTURE_MILESTONE, onUpdateMilestone });
    
    const markCompleteBtn = getByRole('button', { name: 'MARK COMPLETE' });
    await fireEvent.click(markCompleteBtn);
    
    expect(onUpdateMilestone).toHaveBeenCalledWith('m1', { status: 'COMPLETED' });
  });

  it('allows inline editing without prompt', async () => {
    const promptSpy = vi.spyOn(window, 'prompt').mockImplementation(() => 'test');
    const onUpdateMilestone = vi.fn();
    
    const { getByRole, getByPlaceholderText } = render(RoadmapMilestoneCard, { milestone: FIXTURE_MILESTONE, onUpdateMilestone });
    
    const editBtn = getByRole('button', { name: 'Edit Milestone' });
    await fireEvent.click(editBtn);
    
    const titleInput = getByPlaceholderText('Milestone Title');
    await fireEvent.input(titleInput, { target: { value: 'New title' } });
    
    const saveBtn = getByRole('button', { name: 'Save' });
    await fireEvent.click(saveBtn);
    
    expect(promptSpy).not.toHaveBeenCalled();
    expect(onUpdateMilestone).toHaveBeenCalledWith('m1', expect.objectContaining({ title: 'New title' }));
    
    promptSpy.mockRestore();
  });
});
