import { writable } from 'svelte/store';
import type { UserSettingsResponse } from '$lib/api/types';
import type { SettingsProfile } from '../types';
import { deviceTimezone } from '$lib/shared/deviceLocation';
import { normalizeTimezone } from '$lib/shared/timezones';

export const authoritativeSettings = writable<UserSettingsResponse | null>(null);

export function settingsResponseToProfile(
  stored: UserSettingsResponse,
  email = '',
): SettingsProfile {
  return {
    email,
    timezone: normalizeTimezone(stored.timezone || deviceTimezone()),
    focusDurationMinutes: stored.default_focus_minutes ?? 25,
    breakDurationMinutes: stored.default_break_minutes ?? 5,
    startAtLogin: stored.launch_on_startup ?? true,
    keepWidgetOnTop: stored.widget_always_on_top ?? true,
    widgetVisibility: stored.widget_visibility ?? true,
    milestoneReminderLeadTimeMinutes: stored.milestone_reminder_lead_time_minutes ?? 1440,
    quietHoursEnabled: stored.quiet_hours_enabled ?? false,
    quietHoursStart: stored.quiet_hours_start ?? null,
    quietHoursEnd: stored.quiet_hours_end ?? null,
    weatherEnabled: stored.weather_enabled ?? false,
    weatherLocation: stored.weather_location ?? '',
    weatherLocationName: stored.weather_location_name ?? null,
    weatherLat: stored.weather_lat ?? null,
    weatherLon: stored.weather_lon ?? null,
    weatherAnimationEnabled: stored.weather_animation_enabled ?? true,
  };
}
