import { render, screen, waitFor } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { api } from '$lib/api';
import CustomFocusDialog from './CustomFocusDialog.svelte';

vi.mock('$lib/api', () => ({ api: { get: vi.fn(), put: vi.fn() } }));

beforeEach(() => {
  vi.resetAllMocks();
  HTMLDialogElement.prototype.showModal = function () { this.setAttribute('open', ''); };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute('open');
    this.dispatchEvent(new Event('close'));
  };
  vi.mocked(api.get).mockResolvedValue({ default_focus_minutes: 50, default_break_minutes: 10 });
});

describe('CustomFocusDialog', () => {
  it('saves the selected durations and returns them to Today', async () => {
    const onSave = vi.fn();
    vi.mocked(api.put).mockResolvedValue({ default_focus_minutes: 45, default_break_minutes: 15 });
    render(CustomFocusDialog, { open: true, onClose: vi.fn(), onSave });
    const user = userEvent.setup();

    await screen.findByRole('dialog', { name: 'CUSTOM FOCUS TIMER' });
    await waitFor(() => expect(screen.getByLabelText('Focus duration')).toHaveValue('50'));
    await user.selectOptions(screen.getByLabelText('Focus duration'), '45');
    await user.selectOptions(screen.getByLabelText('Break duration'), '15');
    await user.click(screen.getByRole('button', { name: 'Save' }));

    await waitFor(() => expect(api.put).toHaveBeenCalledWith('/me/settings', {
      default_focus_minutes: 45,
      default_break_minutes: 15,
    }));
    expect(onSave).toHaveBeenCalledWith(45, 15);
  });

  it('closes without saving when cancelled', async () => {
    const onClose = vi.fn();
    const onSave = vi.fn();
    render(CustomFocusDialog, { open: true, onClose, onSave });

    await screen.findByRole('dialog', { name: 'CUSTOM FOCUS TIMER' });
    await userEvent.click(screen.getByRole('button', { name: 'Cancel' }));

    expect(onClose).toHaveBeenCalledOnce();
    expect(api.put).not.toHaveBeenCalled();
    expect(onSave).not.toHaveBeenCalled();
  });
});
