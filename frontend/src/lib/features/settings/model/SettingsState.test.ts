import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SettingsState } from './SettingsState.svelte';
import { api } from '$lib/api';
import { desktop } from '$lib/platform/desktopWindow';
import { authoritativeSettings } from './userSettingsMapping';

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
    authoritativeSettings.set(null);
    vi.mocked(api.get).mockResolvedValue(null);
    state = new SettingsState();
  });

  it('initializes with default fixture values', () => {
    expect(state.savedSettings.email).toBe('you@example.com');
    expect(state.savedSettings.widgetVisibility).toBe(true);
    expect(state.savedSettings.quietHoursEnabled).toBe(false);
    expect(state.savedSettings.timezone).toBe(Intl.DateTimeFormat().resolvedOptions().timeZone);
    expect(state.savedSettings.focusDurationMinutes).toBe(25);
    expect(state.savedSettings.breakDurationMinutes).toBe(5);
    expect(state.savedSettings.startAtLogin).toBe(true);
    expect(state.savedSettings.keepWidgetOnTop).toBe(false);
    expect(state.savedSettings.milestoneReminderLeadTimeMinutes).toBe(1440);
  });

  it('calculates dirty state correctly', () => {
    expect(state.isDirty).toBe(false);
    
    state.draftSettings.focusDurationMinutes = 50;
    expect(state.isDirty).toBe(true);

    state.draftSettings.focusDurationMinutes = 25;
    expect(state.isDirty).toBe(false);
  });

  it('cancels changes by reverting draft to saved', () => {
    state.draftSettings.focusDurationMinutes = 50;
    state.cancel();
    expect(state.draftSettings.focusDurationMinutes).toBe(25);
    expect(state.isDirty).toBe(false);
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
    vi.mocked(api.put).mockResolvedValue({
      mr_bloom_display_name: 'Saved Name', timezone: 'Asia/Ho_Chi_Minh',
      default_focus_minutes: 50, default_break_minutes: 10,
      launch_on_startup: true, widget_always_on_top: true,
      milestone_reminder_lead_time_minutes: 1440, weather_enabled: true,
      weather_location: 'Ho Chi Minh City', weather_location_name: 'Ho Chi Minh City, Vietnam',
      weather_lat: 10.82, weather_lon: 106.63, scene_season: 'AUTO',
      weather_animation_enabled: false,
      widget_visibility: true, quiet_hours_enabled: false, quiet_hours_start: null, quiet_hours_end: null,
    });
    const notifyWidget = vi.spyOn(desktop, 'settingsUpdated').mockResolvedValue();
    const reconcile = vi.spyOn(desktop, 'reconcileSettings').mockResolvedValue();
    state.draftSettings.weatherEnabled = true;
    state.draftSettings.weatherLocation = 'Ho Chi Minh City';
    state.draftSettings.weatherLocationName = 'Ho Chi Minh City, Vietnam';
    state.draftSettings.weatherLat = 10.82;
    state.draftSettings.weatherLon = 106.63;
    state.draftSettings.weatherAnimationEnabled = false;
    const success = await state.save();
    
    expect(success).toBe(true);
    expect(state.savedSettings.timezone).toBe('Asia/Ho_Chi_Minh');
    expect(state.savedSettings.focusDurationMinutes).toBe(50);
    expect(state.isDirty).toBe(false);
    expect(api.put).toHaveBeenCalledWith('/me/settings', expect.objectContaining({
      weather_enabled: true,
      weather_location: 'Ho Chi Minh City',
      weather_location_name: 'Ho Chi Minh City, Vietnam',
      weather_lat: 10.82,
      weather_lon: 106.63,
      weather_animation_enabled: false,
      widget_visibility: true, quiet_hours_enabled: false, quiet_hours_start: null, quiet_hours_end: null,
    }));
    expect(api.put).toHaveBeenCalledWith('/me/settings', expect.not.objectContaining({ scene_season: expect.anything() }));
    expect(reconcile).toHaveBeenCalledWith(expect.objectContaining({
      launch_on_startup: true,
      widget_always_on_top: true,
    }));
    expect(notifyWidget).toHaveBeenCalledTimes(1);
    expect(vi.mocked(api.put).mock.invocationCallOrder[0]).toBeLessThan(notifyWidget.mock.invocationCallOrder[0]);
    notifyWidget.mockRestore();
    reconcile.mockRestore();
  });

  it('loads onboarding-persisted values into Settings exactly', () => {
    authoritativeSettings.set({
      mr_bloom_display_name: 'Legacy Name', timezone: 'Europe/Paris',
      default_focus_minutes: 40, default_break_minutes: 8,
      launch_on_startup: false, widget_always_on_top: false,
      milestone_reminder_lead_time_minutes: 60, weather_enabled: true,
      weather_location: null, weather_location_name: 'Paris, France',
      weather_lat: 48.86, weather_lon: 2.35, scene_season: 'WINTER',
      weather_animation_enabled: false,
      widget_visibility: true, quiet_hours_enabled: false, quiet_hours_start: null, quiet_hours_end: null,
    });

    const synced = new SettingsState();

    expect(synced.savedSettings).toMatchObject({
      timezone: 'Europe/Paris', focusDurationMinutes: 40, breakDurationMinutes: 8,
      startAtLogin: false, keepWidgetOnTop: false, weatherEnabled: true,
      weatherLocationName: 'Paris, France', weatherLat: 48.86, weatherLon: 2.35,
    });
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

  it('widget_visibility=false persists before native reconcile', async () => {
    vi.mocked(api.put).mockResolvedValue({
      mr_bloom_display_name: 'Mr. Bloom', timezone: 'UTC',
      default_focus_minutes: 25, default_break_minutes: 5,
      launch_on_startup: true, widget_always_on_top: false,
      milestone_reminder_lead_time_minutes: 1440, weather_enabled: false,
      weather_location: null, weather_location_name: null,
      weather_lat: null, weather_lon: null, scene_season: 'AUTO',
      weather_animation_enabled: true,
      widget_visibility: false, quiet_hours_enabled: false, quiet_hours_start: null, quiet_hours_end: null,
    });
    const reconcile = vi.spyOn(desktop, 'reconcileSettings').mockResolvedValue();
    state.draftSettings.widgetVisibility = false;
    await state.save();
    expect(api.put).toHaveBeenCalledWith('/me/settings', expect.objectContaining({ widget_visibility: false }));
    expect(reconcile).toHaveBeenCalledWith(expect.objectContaining({ widget_visibility: false }));
  });

  it('widget_visibility=true persists before native reconcile', async () => {
    vi.mocked(api.put).mockResolvedValue({
      mr_bloom_display_name: 'Mr. Bloom', timezone: 'UTC',
      default_focus_minutes: 25, default_break_minutes: 5,
      launch_on_startup: true, widget_always_on_top: false,
      milestone_reminder_lead_time_minutes: 1440, weather_enabled: false,
      weather_location: null, weather_location_name: null,
      weather_lat: null, weather_lon: null, scene_season: 'AUTO',
      weather_animation_enabled: true,
      widget_visibility: true, quiet_hours_enabled: false, quiet_hours_start: null, quiet_hours_end: null,
    });
    const reconcile = vi.spyOn(desktop, 'reconcileSettings').mockResolvedValue();
    state.draftSettings.widgetVisibility = true;
    await state.save();
    expect(api.put).toHaveBeenCalledWith('/me/settings', expect.objectContaining({ widget_visibility: true }));
    expect(reconcile).toHaveBeenCalledWith(expect.objectContaining({ widget_visibility: true }));
  });

  it('widget_always_on_top persists before native reconcile', async () => {
    vi.mocked(api.put).mockResolvedValue({
      mr_bloom_display_name: 'Mr. Bloom', timezone: 'UTC',
      default_focus_minutes: 25, default_break_minutes: 5,
      launch_on_startup: true, widget_always_on_top: true,
      milestone_reminder_lead_time_minutes: 1440, weather_enabled: false,
      weather_location: null, weather_location_name: null,
      weather_lat: null, weather_lon: null, scene_season: 'AUTO',
      weather_animation_enabled: true,
      widget_visibility: true, quiet_hours_enabled: false, quiet_hours_start: null, quiet_hours_end: null,
    });
    const reconcile = vi.spyOn(desktop, 'reconcileSettings').mockResolvedValue();
    state.draftSettings.keepWidgetOnTop = true;
    await state.save();
    expect(api.put).toHaveBeenCalledWith('/me/settings', expect.objectContaining({ widget_always_on_top: true }));
    expect(reconcile).toHaveBeenCalledWith(expect.objectContaining({ widget_always_on_top: true }));
  });

  it('launch_on_startup persists before native reconcile', async () => {
    vi.mocked(api.put).mockResolvedValue({
      mr_bloom_display_name: 'Mr. Bloom', timezone: 'UTC',
      default_focus_minutes: 25, default_break_minutes: 5,
      launch_on_startup: true, widget_always_on_top: false,
      milestone_reminder_lead_time_minutes: 1440, weather_enabled: false,
      weather_location: null, weather_location_name: null,
      weather_lat: null, weather_lon: null, scene_season: 'AUTO',
      weather_animation_enabled: true,
      widget_visibility: true, quiet_hours_enabled: false, quiet_hours_start: null, quiet_hours_end: null,
    });
    const reconcile = vi.spyOn(desktop, 'reconcileSettings').mockResolvedValue();
    state.draftSettings.startAtLogin = true;
    await state.save();
    expect(api.put).toHaveBeenCalledWith('/me/settings', expect.objectContaining({ launch_on_startup: true }));
    expect(reconcile).toHaveBeenCalledWith(expect.objectContaining({ launch_on_startup: true }));
  });

  it('backend failure -> native reconcile NOT called', async () => {
    vi.mocked(api.put).mockRejectedValue(new Error('Network error'));
    const reconcile = vi.spyOn(desktop, 'reconcileSettings').mockResolvedValue();
    state.draftSettings.keepWidgetOnTop = true;
    await state.save();
    expect(api.put).toHaveBeenCalled();
    expect(reconcile).not.toHaveBeenCalled();
    expect(state.saveErrorMessage).toBe('Network error');
    expect(state.savedSettings.keepWidgetOnTop).toBe(false);
  });

  it('backend success + native failure -> persisted/local value remains the new backend value and warns', async () => {
    vi.mocked(api.put).mockResolvedValue({
      mr_bloom_display_name: 'Mr. Bloom', timezone: 'UTC',
      default_focus_minutes: 25, default_break_minutes: 5,
      launch_on_startup: true, widget_always_on_top: true,
      milestone_reminder_lead_time_minutes: 1440, weather_enabled: false,
      weather_location: null, weather_location_name: null,
      weather_lat: null, weather_lon: null, scene_season: 'AUTO',
      weather_animation_enabled: true,
      widget_visibility: true, quiet_hours_enabled: false, quiet_hours_start: null, quiet_hours_end: null,
    });
    const reconcile = vi.spyOn(desktop, 'reconcileSettings').mockRejectedValue(new Error('Desktop error'));
    state.draftSettings.keepWidgetOnTop = true;
    await state.save();
    expect(api.put).toHaveBeenCalled();
    expect(reconcile).toHaveBeenCalled();
    expect(state.syncWarning).toBe('Settings saved, but desktop settings could not be synchronized.');
    expect(state.savedSettings.keepWidgetOnTop).toBe(true);
  });

  it('settingsUpdated emitted only after successful backend persistence', async () => {
    vi.mocked(api.put).mockResolvedValue({
      mr_bloom_display_name: 'New Name', timezone: 'UTC',
      default_focus_minutes: 25, default_break_minutes: 5,
      launch_on_startup: true, widget_always_on_top: false,
      milestone_reminder_lead_time_minutes: 1440, weather_enabled: false,
      weather_location: null, weather_location_name: null,
      weather_lat: null, weather_lon: null, scene_season: 'AUTO',
      weather_animation_enabled: true,
      widget_visibility: true, quiet_hours_enabled: false, quiet_hours_start: null, quiet_hours_end: null,
    });
    const notifyWidget = vi.spyOn(desktop, 'settingsUpdated').mockResolvedValue();
    let emitted = false;
    window.addEventListener('blooming:settings-updated', () => emitted = true);
    
    await state.save();
    expect(api.put).toHaveBeenCalled();
    expect(emitted).toBe(true);
    expect(notifyWidget).toHaveBeenCalled();
    
    vi.mocked(api.put).mockRejectedValueOnce(new Error('Fail'));
    emitted = false;
    notifyWidget.mockClear();
    await state.save();
    expect(emitted).toBe(false);
    expect(notifyWidget).not.toHaveBeenCalled();
  });

});
