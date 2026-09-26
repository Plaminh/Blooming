import { fireEvent, render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import axe from 'axe-core';
import { describe, expect, it, vi } from 'vitest';
import type { DesktopWindowService } from '$lib/platform/desktopWindow';
import OnboardingSetupView from './components/pages/OnboardingSetupView.svelte';
import { normalizeTimezone } from '$lib/shared/timezones';

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
    render(OnboardingSetupView, {
      props: { onFinish, initialData: { weatherLocationName: 'Hanoi', weatherLat: 21.03, weatherLon: 105.85 }, windowService: mockWindowService() },
    });

    const timezone = screen.getByRole('combobox', { name: 'Your timezone' });
    const startAtLogin = screen.getByRole('checkbox', { name: 'Start Blooming at login' });
    const keepOnTop = screen.getByRole('checkbox', { name: 'Keep widget on top' });

    expect(screen.queryByLabelText(/Mr\. Bloom.s name/)).not.toBeInTheDocument();
    expect(timezone).not.toHaveValue('');
    expect(startAtLogin).toBeChecked();
    expect(keepOnTop).toBeChecked();

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

    await user.click(screen.getByRole('button', { name: 'FINISH' }));

    expect(screen.queryByRole('button', { name: 'BACK' })).not.toBeInTheDocument();
    expect(onFinish).toHaveBeenCalledWith({
      timezone: normalizeTimezone(Intl.DateTimeFormat().resolvedOptions().timeZone),
      weatherLocation: '',
      weatherLocationName: 'Hanoi',
      weatherLat: 21.03,
      weatherLon: 105.85,
      focusPreset: '50 / 10',
      focusMinutes: 50,
      breakMinutes: 10,
      startAtLogin: false,
      keepWidgetOnTop: true,
    });
  });

  it('disables form controls while submission is pending', async () => {
    const user = userEvent.setup();
    let resolveFinish: () => void;
    const finishPromise = new Promise<void>((resolve) => {
      resolveFinish = resolve;
    });
    const onFinish = vi.fn().mockReturnValue(finishPromise);
    render(OnboardingSetupView, {
      props: { onFinish, initialData: { weatherLocationName: 'Hanoi', weatherLat: 21.03, weatherLon: 105.85 }, windowService: mockWindowService() },
    });

    const finishButton = screen.getByRole('button', { name: 'FINISH' });

    await user.click(finishButton);
    await fireEvent.submit(screen.getByRole('form', { name: 'Blooming setup' }));
    expect(onFinish).toHaveBeenCalledTimes(1);

    expect(finishButton).toBeDisabled();
    expect(screen.getByRole('combobox', { name: 'Your timezone' })).toBeDisabled();

    // Resolve the promise
    resolveFinish!();
    
    // We need to wait for the next tick for the UI to update
    await new Promise((r) => setTimeout(r, 0));

    expect(screen.getByRole('combobox', { name: 'Your timezone' })).not.toBeDisabled();
    expect(finishButton).not.toBeDisabled();
  });

  it('removes the misleading stepper and preserves keyboard-operable controls', async () => {
    const user = userEvent.setup();
    render(OnboardingSetupView, { props: { windowService: mockWindowService() } });

    expect(screen.queryByRole('navigation', { name: 'Onboarding progress' })).not.toBeInTheDocument();
    expect(document.querySelector('.setup-form-container')).toHaveAttribute('data-scrollable', 'true');
    const custom = screen.getByRole('button', { name: 'CUSTOM' });
    custom.focus();
    await user.keyboard('{Enter}');
    expect(custom).toHaveAttribute('aria-pressed', 'true');

    const checkbox = screen.getByRole('checkbox', { name: 'Keep widget on top' });
    checkbox.focus();
    await user.keyboard(' ');
    expect(checkbox).not.toBeChecked();
  });

  it('restores saved values without replacing the timezone with the device default', () => {
    render(OnboardingSetupView, {
      props: {
        initialData: {
          timezone: 'Europe/Paris', focusPreset: 'CUSTOM',
          focusMinutes: 40, breakMinutes: 8, weatherLocationName: 'Paris, France',
          weatherLat: 48.86, weatherLon: 2.35, startAtLogin: false, keepWidgetOnTop: false,
        },
        windowService: mockWindowService(),
      },
    });
    expect(screen.getByRole('combobox', { name: 'Your timezone' })).toHaveValue('Europe/Paris');
    expect(screen.getByRole('spinbutton', { name: 'Focus minutes' })).toHaveValue(40);
    expect(screen.getByRole('combobox', { name: 'Search weather location' })).toHaveValue('Paris, France');
  });

  it('keeps form values and stays interactive after a failed save', async () => {
    const user = userEvent.setup();
    const onFinish = vi.fn().mockRejectedValue(new Error('Settings could not be saved.'));
    render(OnboardingSetupView, { props: { onFinish, initialData: { weatherLocationName: 'Hanoi', weatherLat: 21.03, weatherLon: 105.85 }, windowService: mockWindowService() } });
    await user.click(screen.getByRole('button', { name: '50 / 10' }));
    await user.click(screen.getByRole('button', { name: 'FINISH' }));
    expect(await screen.findByText('Settings could not be saved.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '50 / 10' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('button', { name: 'FINISH' })).toBeEnabled();
  });

  it('validates and submits custom focus values', async () => {
    const user = userEvent.setup();
    const onFinish = vi.fn();
    render(OnboardingSetupView, { props: { onFinish, initialData: { weatherLocationName: 'Hanoi', weatherLat: 21.03, weatherLon: 105.85 }, windowService: mockWindowService() } });
    await user.click(screen.getByRole('button', { name: 'CUSTOM' }));
    const focus = screen.getByRole('spinbutton', { name: 'Focus minutes' });
    await user.clear(focus);
    await user.type(focus, '0');
    expect(screen.getByRole('button', { name: 'FINISH' })).toBeDisabled();
    expect(onFinish).not.toHaveBeenCalled();
    await user.clear(focus);
    await user.type(focus, '45');
    expect(screen.getByRole('button', { name: 'FINISH' })).toBeEnabled();
    await user.click(screen.getByRole('button', { name: 'FINISH' }));
    expect(onFinish).toHaveBeenCalledWith(expect.objectContaining({ focusPreset: 'CUSTOM', focusMinutes: 45, breakMinutes: 5 }));
  });

  it('never finishes through implicit Enter submission', async () => {
    const user = userEvent.setup();
    const onFinish = vi.fn();
    render(OnboardingSetupView, { props: { onFinish, initialData: { weatherLocationName: 'Hanoi', weatherLat: 21.03, weatherLon: 105.85 }, windowService: mockWindowService() } });
    const timezone = screen.getByRole('combobox', { name: 'Your timezone' });
    timezone.focus();
    await user.keyboard('{Enter}');
    expect(onFinish).not.toHaveBeenCalled();
    const weather = screen.getByRole('combobox', { name: 'Search weather location' });
    weather.focus();
    await user.keyboard('{Enter}');
    expect(onFinish).not.toHaveBeenCalled();
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
