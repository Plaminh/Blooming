import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import RightRail from './RightRail.svelte';
import type { Task } from '$lib/features/today/types';

const mockUpcomingTask: Task = {
  id: 'block-1',
  task_id: 'task-1',
  title: 'Write Documentation',
  startTime: '09:00',
  endTime: '10:00',
  durationString: '(60 min)',
  estimatedDurationMinutes: 60,
  status: 'upcoming',
  category: 'Work',
  iconRef: 'document',
  description: 'Write API documentation and guides.',
  notes: 'Important reference links in wiki.'
};

const mockCompletedTask: Task = {
  id: 'block-2',
  task_id: 'task-2',
  title: 'Review PRs',
  startTime: '10:00',
  endTime: '10:30',
  durationString: '(30 min)',
  estimatedDurationMinutes: 30,
  status: 'completed',
  category: 'Work',
  iconRef: 'document',
  description: 'Review pending code reviews.',
  notes: 'Review pending code reviews.'
};

describe('RightRail (Execution-Only Read-Only Inspector)', () => {
  const onPresetSelect = vi.fn();
  const onCustomSaved = vi.fn();
  const onStartFocus = vi.fn();
  const onMarkComplete = vi.fn();
  const onAdjustWithMrBloom = vi.fn();

  beforeEach(() => {
    vi.resetAllMocks();
  });

  function renderRail(task?: Task) {
    return render(RightRail, {
      task,
      nextTask: undefined,
      selectedFocusPreset: '25/5',
      customFocusMinutes: 25,
      customBreakMinutes: 5,
      focusDisabled: false,
      onPresetSelect,
      onCustomSaved,
      onStartFocus,
      onMarkComplete,
      onAdjustWithMrBloom
    });
  }

  it('renders task details strictly as read-only text without edit inputs or edit toggle', () => {
    renderRail(mockUpcomingTask);

    // Title and duration
    expect(screen.getByRole('heading', { level: 3, name: 'Write Documentation' })).toBeInTheDocument();
    expect(screen.getByText(/09:00 – 10:00/)).toBeInTheDocument();
    expect(screen.getByText(/\(60 min\)/)).toBeInTheDocument();

    // Category and notes
    expect(screen.getByText('Work')).toBeInTheDocument();
    expect(screen.getByText('Write API documentation and guides.')).toBeInTheDocument();
    expect(screen.getByText('Important reference links in wiki.')).toBeInTheDocument();

    // Verify ABSENCE of edit toggle, input elements, category dropdown, textarea
    expect(screen.queryByLabelText(/Edit task/i)).not.toBeInTheDocument();
    expect(screen.queryByRole('textbox', { name: /Title/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('spinbutton', { name: /Duration/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('combobox', { name: /Category/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('textbox', { name: /Notes/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /^Save$/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /^Cancel$/i })).not.toBeInTheDocument();

    // Verify ABSENCE of direct Delete button
    expect(screen.queryByRole('button', { name: /Delete/i })).not.toBeInTheDocument();
  });

  it('renders START FOCUS action and triggers handler when clicked', async () => {
    renderRail(mockUpcomingTask);

    const startFocusBtn = screen.getByRole('button', { name: /START FOCUS/i });
    expect(startFocusBtn).toBeInTheDocument();
    expect(startFocusBtn).not.toBeDisabled();

    await fireEvent.click(startFocusBtn);
    expect(onStartFocus).toHaveBeenCalledOnce();
  });

  it('renders MARK COMPLETE action and handles task completion', async () => {
    renderRail(mockUpcomingTask);

    const markCompleteBtn = screen.getByRole('button', { name: /MARK COMPLETE/i });
    expect(markCompleteBtn).toBeInTheDocument();
    expect(markCompleteBtn).not.toBeDisabled();

    await fireEvent.click(markCompleteBtn);
    expect(onMarkComplete).toHaveBeenCalledWith('task-1');
  });

  it('disables MARK COMPLETE and START FOCUS when task is already completed', () => {
    renderRail(mockCompletedTask);

    const markCompleteBtn = screen.getByRole('button', { name: /COMPLETED/i });
    expect(markCompleteBtn).toBeDisabled();

    const startFocusBtn = screen.getByRole('button', { name: /START FOCUS/i });
    expect(startFocusBtn).toBeDisabled();
  });

  it('renders ADJUST WITH MR. BLOOM and triggers navigation callback', async () => {
    renderRail(mockUpcomingTask);

    const adjustBtn = screen.getByRole('button', { name: /ADJUST WITH MR\. BLOOM/i });
    expect(adjustBtn).toBeInTheDocument();

    await fireEvent.click(adjustBtn);
    expect(onAdjustWithMrBloom).toHaveBeenCalledWith('task-1');
  });

  it('renders empty state when no task is selected', () => {
    renderRail(undefined);
    expect(screen.getByText(/No task selected\./i)).toBeInTheDocument();
  });
});
