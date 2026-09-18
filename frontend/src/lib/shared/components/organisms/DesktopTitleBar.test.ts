import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import DesktopTitleBar from './DesktopTitleBar.svelte';

it('uses the garden close action and hides the size controls', async () => {
  const onClose = vi.fn();
  const windowService = {
    openMainWindow: vi.fn(),
    minimizeCurrent: vi.fn(),
    toggleMaximizeCurrent: vi.fn().mockResolvedValue(false),
    isCurrentMaximized: vi.fn().mockResolvedValue(false),
    hideCurrent: vi.fn(),
    closeCurrent: vi.fn(),
    startDraggingCurrent: vi.fn(),
  };

  render(DesktopTitleBar, { showSizeControls: false, onClose, windowService });

  expect(screen.queryByRole('button', { name: 'Minimize window' })).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Maximize window' })).not.toBeInTheDocument();
  await userEvent.click(screen.getByRole('button', { name: 'Close window' }));
  expect(onClose).toHaveBeenCalledOnce();
  expect(windowService.hideCurrent).not.toHaveBeenCalled();
});
