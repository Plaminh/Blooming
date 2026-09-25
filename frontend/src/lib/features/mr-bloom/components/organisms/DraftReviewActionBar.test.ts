import { expect, test, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import DraftReviewActionBar from './DraftReviewActionBar.svelte';

test('disables both primary and secondary actions while an operation is pending', async () => {
  const onPrimary = vi.fn();
  const onSecondary = vi.fn();
  render(DraftReviewActionBar, {
    primaryLabel: 'SAVE', secondaryLabel: 'DISCARD',
    onPrimary, onSecondary, disabled: true
  });

  const primary = screen.getByRole('button', { name: 'SAVE' });
  const secondary = screen.getByRole('button', { name: 'DISCARD' });
  expect(primary).toBeDisabled();
  expect(secondary).toBeDisabled();
});
