import { render, screen, fireEvent } from '@testing-library/svelte';
import { tick } from 'svelte';
import { afterEach, expect, it, vi } from 'vitest';
import GeneralPanel from './GeneralPanel.svelte';
import { api } from '$lib/api';

const state = vi.hoisted(() => ({
  savedSettings: { weatherLocationName: 'Saved City', weatherLocation: '', timezone: 'UTC' },
  draftSettings: {
    mrBloomName: 'Bloom', weatherLocationName: 'Saved City' as string | null,
    weatherLat: 1 as number | null, weatherLon: 2 as number | null,
    sceneSeason: 'AUTO', weatherEnabled: true, weatherAnimationEnabled: true,
    startAtLogin: false, keepWidgetOnTop: false,
  },
  validationErrors: {} as Record<string, string>,
}));
vi.mock('$lib/features/settings/model/SettingsState.svelte', () => ({ getSettingsState: () => state }));
vi.mock('$lib/api', () => ({ api: { get: vi.fn() } }));
afterEach(() => vi.useRealTimers());

it('keeps the saved place visible while editing invalidates the draft', async () => {
  vi.useFakeTimers();
  vi.mocked(api.get).mockResolvedValue({ candidates: [{ name: 'New City', lat: 3, lon: 4 }] });
  render(GeneralPanel);
  expect(screen.getByText('Saved City')).toBeInTheDocument();
  await fireEvent.input(screen.getByRole('textbox', { name: 'Search weather location' }), { target: { value: 'New' } });
  expect(state.draftSettings.weatherLocationName).toBeNull();
  expect(state.draftSettings.weatherLat).toBeNull();
  expect(state.draftSettings.weatherLon).toBeNull();
  expect(screen.getByText('Saved City')).toBeInTheDocument();
  await vi.advanceTimersByTimeAsync(500);
  await tick();
  await fireEvent.click(screen.getByRole('button', { name: 'New City' }));
  expect(state.draftSettings.weatherLocationName).toBe('New City');
  expect(state.draftSettings.weatherLat).toBe(3);
  expect(state.draftSettings.weatherLon).toBe(4);
});
