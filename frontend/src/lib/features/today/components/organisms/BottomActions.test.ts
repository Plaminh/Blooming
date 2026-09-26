import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import BottomActions from './BottomActions.svelte';

describe('BottomActions (Execution-Only Dashboard)', () => {
  it('renders QUICK REPLAN and ADJUST WITH MR. BLOOM and no EDIT MANUALLY', async () => {
    const onQuickReplan = vi.fn();
    const onAdjustWithMrBloom = vi.fn();

    render(BottomActions, {
      disabled: false,
      onQuickReplan,
      onAdjustWithMrBloom
    });

    // EDIT MANUALLY must NOT exist
    expect(screen.queryByRole('button', { name: /EDIT MANUALLY/i })).not.toBeInTheDocument();

    // QUICK REPLAN
    const quickReplanBtn = screen.getByRole('button', { name: /QUICK REPLAN/i });
    expect(quickReplanBtn).toBeInTheDocument();
    await fireEvent.click(quickReplanBtn);
    expect(onQuickReplan).toHaveBeenCalledOnce();

    // ADJUST WITH MR. BLOOM
    const adjustBtn = screen.getByRole('button', { name: /ADJUST WITH MR\. BLOOM/i });
    expect(adjustBtn).toBeInTheDocument();
    await fireEvent.click(adjustBtn);
    expect(onAdjustWithMrBloom).toHaveBeenCalledOnce();
  });

  it('disables buttons when disabled prop is true', () => {
    render(BottomActions, {
      disabled: true,
      onQuickReplan: vi.fn(),
      onAdjustWithMrBloom: vi.fn()
    });

    expect(screen.getByRole('button', { name: /QUICK REPLAN/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /ADJUST WITH MR\. BLOOM/i })).toBeDisabled();
  });
});
