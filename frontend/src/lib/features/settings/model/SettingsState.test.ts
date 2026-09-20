import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SettingsState } from './SettingsState.svelte';
import { api } from '$lib/api';
import { desktop } from '$lib/platform/desktopWindow';

vi.mock('$lib/api', () => ({
  api: {
    get: vi.fn().mockResolvedValue(null),
    put: vi.fn().mockResolvedValue({})
  },
  setAuthErrorHandler: vi.fn()
}));

vi.mock('@tauri-apps/api/window', () => ({
  Window: {
    getByLabel: vi.fn().mockResolvedValue(null)
  }
}));

vi.mock('$lib/shared/stores/authStore', () => ({
  authStore: {
    subscribe: (cb: any) => { cb({ user: { email: 'you@example.com' } }); return () => {}; },
    clearAuth: vi.fn()
  }
}));


describe('SettingsState', () => {
  let state: SettingsState;

  beforeEach(() => {
    vi.clearAllMocks();
    state = new SettingsState();
  });

  it('initializes with default fixture values', () => {
    expect(state.savedSettings.email).toBe('you@example.com');
    expect(state.savedSettings.mrBloomName).toBe('Mr. Bloom');
    expect(state.savedSettings.timezone).toBe(Intl.DateTimeFormat().resolvedOptions().timeZone);
    expect(state.savedSettings.focusDurationMinutes).toBe(25);
    expect(state.savedSettings.breakDurationMinutes).toBe(5);
    expect(state.savedSettings.startAtLogin).toBe(true);
    expect(state.savedSettings.keepWidgetOnTop).toBe(true);
    expect(state.savedSettings.milestoneReminderLeadTimeMinutes).toBe(1440);
    expect(state.savedSettings.emailReminders).toBe(true);
  });

  it('calculates dirty state correctly', () => {
    expect(state.isDirty).toBe(false);
    
    state.draftSettings.mrBloomName = 'New Name';
    expect(state.isDirty).toBe(true);
    
    state.draftSettings.mrBloomName = 'Mr. Bloom';
    expect(state.isDirty).toBe(false);
  });

  it('cancels changes by reverting draft to saved', () => {
    state.draftSettings.mrBloomName = 'Discarded Name';
    state.cancel();
    expect(state.draftSettings.mrBloomName).toBe('Mr. Bloom');
    expect(state.isDirty).toBe(false);
  });

  it('validates name length and emptiness', () => {
    state.draftSettings.mrBloomName = '   ';
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.mrBloomName).toBeDefined();

    state.draftSettings.mrBloomName = 'A'.repeat(61);
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.mrBloomName).toBeDefined();

    state.draftSettings.mrBloomName = 'Valid Name';
    expect(state.validate()).toBe(true);
  });

  it('validates duration bounds', () => {
    state.draftSettings.focusDurationMinutes = 0;
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.focusDurationMinutes).toBeDefined();

    state.draftSettings.focusDurationMinutes = 25;
    state.draftSettings.breakDurationMinutes = -5;
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.breakDurationMinutes).toBeDefined();
  });

  it('validates reminder lead time', () => {
    state.draftSettings.milestoneReminderLeadTimeMinutes = NaN;
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.milestoneReminderLeadTimeMinutes).toBeDefined();

    state.draftSettings.milestoneReminderLeadTimeMinutes = -1;
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.milestoneReminderLeadTimeMinutes).toBeDefined();

    state.draftSettings.milestoneReminderLeadTimeMinutes = 60;
    expect(state.validate()).toBe(true);
  });

  it('saves successfully', async () => {
    const notifyWidget = vi.spyOn(desktop, 'settingsUpdated').mockResolvedValue();
    state.draftSettings.mrBloomName = 'Saved Name';
    state.draftSettings.weatherEnabled = true;
    state.draftSettings.weatherLocation = 'Ho Chi Minh City';
    state.draftSettings.weatherLocationName = 'Ho Chi Minh City, Vietnam';
    state.draftSettings.weatherLat = 10.82;
    state.draftSettings.weatherLon = 106.63;
    state.draftSettings.weatherAnimationEnabled = false;
    const success = await state.save();
    
    expect(success).toBe(true);
    expect(state.savedSettings.mrBloomName).toBe('Saved Name');
    expect(state.isDirty).toBe(false);
    expect(api.put).toHaveBeenCalledWith('/me/settings', expect.objectContaining({
      weather_enabled: true,
      weather_location: 'Ho Chi Minh City',
      weather_location_name: 'Ho Chi Minh City, Vietnam',
      weather_lat: 10.82,
      weather_lon: 106.63,
      weather_animation_enabled: false,
    }));
    expect(notifyWidget).toHaveBeenCalledTimes(1);
    expect(vi.mocked(api.put).mock.invocationCallOrder[0]).toBeLessThan(notifyWidget.mock.invocationCallOrder[0]);
    notifyWidget.mockRestore();
  });

  it('rejects free text and restores the saved selection on cancel', () => {
    state.savedSettings.weatherLocationName = 'Saved City';
    state.savedSettings.weatherLat = 1;
    state.savedSettings.weatherLon = 2;
    state.draftSettings.weatherEnabled = true;
    state.draftSettings.weatherLocationName = null;
    state.draftSettings.weatherLat = null;
    state.draftSettings.weatherLon = null;
    state.draftSettings.weatherLocation = 'Typed only';
    expect(state.validate()).toBe(false);
    const version = state.locationPickerVersion;
    state.cancel();
    expect(state.draftSettings.weatherLocationName).toBe('Saved City');
    expect(state.draftSettings.weatherLat).toBe(1);
    expect(state.draftSettings.weatherLon).toBe(2);
    expect(state.locationPickerVersion).toBe(version + 1);
  });
});
