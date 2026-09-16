import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import TodayPage from "../../../routes/(app)/today/+page.svelte";

describe('Today Screen Feature', () => {
  it('renders the initial formatted displayed date correctly', () => {
    render(TodayPage);
    // Apr 23, 2024 is the initial state
    expect(screen.getByText('Tue, Apr 23, 2024')).toBeInTheDocument();
  });

  it('handles date transitions (previous/next/today) and empty-day state', async () => {
    render(TodayPage);
    const prevBtn = screen.getByLabelText('Previous day');
    const nextBtn = screen.getByLabelText('Next day');
    const todayBtn = screen.getByText('Today');

    // Move to next day (Apr 24)
    await fireEvent.click(nextBtn);
    expect(screen.getByText('Wed, Apr 24, 2024')).toBeInTheDocument();
    
    // Day without mock tasks shows empty state
    expect(screen.getByText('No tasks scheduled for this day.')).toBeInTheDocument();

    // Move to previous day (Apr 23)
    await fireEvent.click(prevBtn);
    expect(screen.getByText('Tue, Apr 23, 2024')).toBeInTheDocument();
    
    // Jump to Today (current system date)
    await fireEvent.click(todayBtn);
    // Should show empty state since it's not the demo day
    expect(screen.getByText('No tasks scheduled for this day.')).toBeInTheDocument();
  });

  it('supports task selection and Task Details derivation', async () => {
    render(TodayPage);
    // Go to demo date implicitly by reloading
    // Or just check since first render is the demo date
    
    const taskButton = screen.getByText('Finish proposal');
    await fireEvent.click(taskButton);
    
    // The Task Details panel should update to show its category
    expect(screen.getByText('Work')).toBeInTheDocument(); // Category
  });

  it('supports single focus-preset selection and Start Focus local action', async () => {
    render(TodayPage);
    
    // 25/5 is selected by default
    const preset50 = screen.getByText('50/10');
    await fireEvent.click(preset50);
    
    // The Start Focus button should be enabled because a task is selected by default (Task 1)
    const startFocusBtn = screen.getByText(/START FOCUS/);
    expect(startFocusBtn).not.toBeDisabled();
    
    await fireEvent.click(startFocusBtn);
    // Start focus changes a local state variable, we can't easily assert it unless it shows in UI, but we can verify it doesn't crash
  });
});
