import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import axe from 'axe-core';
import { describe, expect, it, vi } from 'vitest';
import type { DesktopWindowService } from '$lib/platform/desktopWindow';
import OnboardingSetupView from './components/pages/OnboardingSetupView.svelte';

function mockWindowService(): DesktopWindowService {
  return {
    openMainWindow: vi.fn().mockResolvedValue(undefined),
    minimizeCurrent: vi.fn().mockResolvedValue(undefined),
    toggleMaximizeCurrent: vi.fn().mockResolvedValue(false),
    isCurrentMaximized: vi.fn().mockResolvedValue(false),
    hideCurrent: vi.fn().mockResolvedValue(undefined),
    closeCurrent: vi.fn().mockResolvedValue(undefined),
    startDraggingCurrent: vi.fn().mockResolvedValue(undefined),
  };
}

describe('OnboardingSetupView', () => {
  it('updates local setup state and submits the complete current value', async () => {
    const user = userEvent.setup();
    const onFinish = vi.fn();
    const onBack = vi.fn();
    render(OnboardingSetupView, {
      props: { onFinish, onBack, windowService: mockWindowService() },
    });

    const name = screen.getByRole('textbox', { name: 'Mr. Bloom’s name' });
    const timezone = screen.getByRole('combobox', { name: 'Your timezone' });
    const startAtLogin = screen.getByRole('checkbox', { name: 'Start Blooming at login' });
    const keepOnTop = screen.getByRole('checkbox', { name: 'Keep widget on top' });

    expect(name).toHaveValue('Mr. Bloom');
    expect(timezone).toHaveValue('Asia/Ho_Chi_Minh');
    expect(startAtLogin).toBeChecked();
    expect(keepOnTop).toBeChecked();

    await user.clear(name);
    await user.type(name, 'Sprout');
    await user.selectOptions(timezone, 'Europe/London');
    await user.click(screen.getByRole('button', { name: '50 / 10' }));
    await user.click(startAtLogin);

    expect(screen.getByRole('button', { name: '25 / 5' })).toHaveAttribute(
      'aria-pressed',
      'false',
    );
    expect(screen.getByRole('button', { name: '50 / 10' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    expect(screen.getByText('Work for 50 minutes, take a 10-minute break.')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'BACK' }));
    await user.click(screen.getByRole('button', { name: 'FINISH' }));

    expect(onBack).toHaveBeenCalledTimes(1);
    expect(onFinish).toHaveBeenCalledWith({
      name: 'Sprout',
      timezone: 'Europe/London',
      focusPreset: '50 / 10',
      startAtLogin: false,
      keepWidgetOnTop: true,
    });
  });

  it('exposes the active step and preserves keyboard-operable controls', async () => {
    const user = userEvent.setup();
    render(OnboardingSetupView, { props: { windowService: mockWindowService() } });

    expect(screen.getByText('1')).toHaveAttribute('aria-current', 'step');
    const custom = screen.getByRole('button', { name: 'CUSTOM' });
    custom.focus();
    await user.keyboard('{Enter}');
    expect(custom).toHaveAttribute('aria-pressed', 'true');

    const checkbox = screen.getByRole('checkbox', { name: 'Keep widget on top' });
    checkbox.focus();
    await user.keyboard(' ');
    expect(checkbox).not.toBeChecked();
  });

  it('keeps desktop chrome functional and has no axe violations', async () => {
    const user = userEvent.setup();
    const windowService = mockWindowService();
    const { container } = render(OnboardingSetupView, { props: { windowService } });

    await user.click(screen.getByRole('button', { name: 'Minimize window' }));
    await user.click(screen.getByRole('button', { name: 'Maximize window' }));
    await user.click(screen.getByRole('button', { name: 'Close window' }));

    expect(windowService.minimizeCurrent).toHaveBeenCalledTimes(1);
    expect(windowService.toggleMaximizeCurrent).toHaveBeenCalledTimes(1);
    expect(windowService.hideCurrent).toHaveBeenCalledTimes(1);
    expect((await axe.run(container)).violations).toEqual([]);
  });
});
