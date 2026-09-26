import { describe, expect, it } from 'vitest';
import { deriveFocusPreset, settingsResponseToOnboarding, settingsResponseToProfile } from './userSettingsMapping';
import type { UserSettingsResponse } from '$lib/api/types';

const response: UserSettingsResponse = {
  mr_bloom_display_name: 'Mr. Bloom', timezone: 'Asia/Ho_Chi_Minh',
  default_focus_minutes: 45, default_break_minutes: 0,
  launch_on_startup: true, widget_always_on_top: true,
  milestone_reminder_lead_time_minutes: 1440, weather_enabled: true,
  weather_location: null, weather_location_name: 'Ho Chi Minh City, Vietnam',
  weather_lat: 10.82, weather_lon: 106.63, scene_season: 'AUTO',
  weather_animation_enabled: true,
};

describe('user settings mapping', () => {
  it('derives presets from authoritative numeric values', () => {
    expect(deriveFocusPreset(25, 5)).toBe('25 / 5');
    expect(deriveFocusPreset(50, 10)).toBe('50 / 10');
    expect(deriveFocusPreset(45, 15)).toBe('CUSTOM');
  });

  it('maps the same persisted fields into onboarding and Settings without overwriting zero', () => {
    const onboarding = settingsResponseToOnboarding(response);
    const settings = settingsResponseToProfile(response);
    expect(onboarding).toMatchObject({ timezone: 'Asia/Ho_Chi_Minh', focusPreset: 'CUSTOM', focusMinutes: 45, breakMinutes: 0, weatherLocationName: 'Ho Chi Minh City, Vietnam', startAtLogin: true, keepWidgetOnTop: true });
    expect(settings).toMatchObject({ timezone: 'Asia/Ho_Chi_Minh', focusDurationMinutes: 45, breakDurationMinutes: 0, weatherLocationName: 'Ho Chi Minh City, Vietnam', startAtLogin: true, keepWidgetOnTop: true });
  });
});
