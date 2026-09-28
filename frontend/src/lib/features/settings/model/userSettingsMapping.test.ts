import { describe, expect, it } from 'vitest';
import { settingsResponseToProfile } from './userSettingsMapping';
import type { UserSettingsResponse } from '$lib/api/types';

const response: UserSettingsResponse = {
  timezone: 'Asia/Ho_Chi_Minh',
  weather_location_name: 'Ho Chi Minh City, Vietnam',
  weather_lat: 10.823,
  weather_lon: 106.6296,
  default_focus_minutes: 45,
  default_break_minutes: 0,
  launch_on_startup: true,
  widget_always_on_top: true,
  milestone_reminder_lead_time_minutes: 1440,
  weather_enabled: true,
  weather_location: null,
  scene_season: 'AUTO',
  weather_animation_enabled: true,
  widget_visibility: true,
  quiet_hours_enabled: false,
  quiet_hours_start: null,
  quiet_hours_end: null
};

describe('settings mapper', () => {
  it('maps settings properly', () => {
    const settings = settingsResponseToProfile(response);
    expect(settings).toMatchObject({ timezone: 'Asia/Ho_Chi_Minh', focusDurationMinutes: 45, breakDurationMinutes: 0, weatherLocationName: 'Ho Chi Minh City, Vietnam', startAtLogin: true, keepWidgetOnTop: true });
    expect(settings).not.toHaveProperty('mrBloomName');
    expect(settings).not.toHaveProperty('sceneSeason');
    expect(settings).not.toHaveProperty('emailReminders');
  });
});
