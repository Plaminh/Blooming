import type { UserSettingsResponse } from '$lib/api/types';
import type { FocusPreset, OnboardingSetupData } from './OnboardingSetupState.svelte';
import { deviceTimezone } from '$lib/shared/deviceLocation';
import { normalizeTimezone } from '$lib/shared/timezones';

export function deriveFocusPreset(focus: number, rest: number): FocusPreset {
  if (focus === 25 && rest === 5) return '25 / 5';
  if (focus === 50 && rest === 10) return '50 / 10';
  return 'CUSTOM';
}

export function settingsResponseToOnboarding(stored: UserSettingsResponse): Partial<OnboardingSetupData> {
  return {
    timezone: normalizeTimezone(stored.timezone || deviceTimezone()),
    focusPreset: deriveFocusPreset(stored.default_focus_minutes, stored.default_break_minutes),
    focusMinutes: stored.default_focus_minutes,
    breakMinutes: stored.default_break_minutes,
    startAtLogin: stored.launch_on_startup,
    keepWidgetOnTop: stored.widget_always_on_top,
    weatherLocation: stored.weather_location ?? '',
    weatherLocationName: stored.weather_location_name,
    weatherLat: stored.weather_lat,
    weatherLon: stored.weather_lon,
  };
}

export function onboardingToSettingsPayload(data: OnboardingSetupData) {
  return {
    timezone: normalizeTimezone(data.timezone),
    default_focus_minutes: data.focusMinutes,
    default_break_minutes: data.breakMinutes,
    launch_on_startup: data.startAtLogin,
    widget_always_on_top: data.keepWidgetOnTop,
    weather_location_name: data.weatherLocationName,
    weather_lat: data.weatherLat,
    weather_lon: data.weatherLon,
    weather_enabled: data.weatherLat !== null && data.weatherLon !== null,
  };
}

