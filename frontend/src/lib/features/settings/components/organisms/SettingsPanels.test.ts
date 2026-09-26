import { render, screen } from '@testing-library/svelte';
import { expect, it, vi } from 'vitest';
import DesktopPanel from './DesktopPanel.svelte';
import NotificationsPanel from './NotificationsPanel.svelte';

const state = vi.hoisted(() => ({
  draftSettings: {
    startAtLogin: false,
    keepWidgetOnTop: true,
    milestoneReminderLeadTimeMinutes: 1440,
  },
  validationErrors: {} as Record<string, string>,
}));

vi.mock('$lib/features/settings/model/SettingsState.svelte', () => ({
  getSettingsState: () => state,
}));

it('shows desktop controls in a dedicated panel', () => {
  render(DesktopPanel);
  expect(screen.getByRole('heading', { name: 'DESKTOP' })).toBeInTheDocument();
  expect(screen.getByRole('switch', { name: 'Start Blooming at login' })).toBeInTheDocument();
  expect(screen.getByRole('switch', { name: 'Keep widget on top' })).toBeInTheDocument();
});

it('keeps milestone reminders without email reminders', () => {
  render(NotificationsPanel);
  expect(screen.getByRole('combobox', { name: 'Milestone reminder' })).toBeInTheDocument();
  expect(screen.queryByRole('switch', { name: 'Email reminders' })).not.toBeInTheDocument();
});
