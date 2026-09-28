import { describe, expect, it } from 'vitest';
import { deriveFocusPreset, settingsResponseToOnboarding, onboardingToSettingsPayload } from './mappers';
import type { UserSettingsResponse } from '$lib/api/types';

const response: UserSettingsResponse = {
  timezone: 'Asia/Ho_Chi_Minh',
  default_focus_minutes: 45, default_break_minutes: 0,
  launch_on_startup: true, widget_always_on_top: true,
  milestone_reminder_lead_time_minutes: 1440, weather_enabled: true,
  weather_location: null, weather_location_name: 'Ho Chi Minh City, Vietnam',
  weather_lat: 10.82, weather_lon: 106.63, scene_season: 'AUTO',
  weather_animation_enabled: true,
  widget_visibility: true, quiet_hours_enabled: false, quiet_hours_start: null, quiet_hours_end: null,
};

describe('user settings mapping', () => {
  it('derives presets from authoritative numeric values', () => {
    expect(deriveFocusPreset(25, 5)).toBe('25 / 5');
    expect(deriveFocusPreset(50, 10)).toBe('50 / 10');
    expect(deriveFocusPreset(45, 15)).toBe('CUSTOM');
  });

  it('maps the same persisted fields into onboarding without overwriting zero', () => {
    const onboarding = settingsResponseToOnboarding(response);
    expect(onboarding).toMatchObject({ timezone: 'Asia/Ho_Chi_Minh', focusPreset: 'CUSTOM', focusMinutes: 45, breakMinutes: 0, weatherLocationName: 'Ho Chi Minh City, Vietnam', startAtLogin: true, keepWidgetOnTop: true });
  });
});

