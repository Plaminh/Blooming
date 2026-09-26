import { isValidTimezone } from '$lib/shared/timezones';
import type { OnboardingSetupData } from './OnboardingSetupState.svelte';

export type OnboardingErrors = Partial<Record<'timezone' | 'weatherLocation' | 'focusMinutes' | 'breakMinutes', string>>;

export function validateOnboarding(data: OnboardingSetupData): OnboardingErrors {
  const errors: OnboardingErrors = {};
  if (!isValidTimezone(data.timezone)) errors.timezone = 'Select a valid IANA timezone.';
  if (!data.weatherLocationName?.trim() || data.weatherLat === null || data.weatherLon === null)
    errors.weatherLocation = 'Select a city or use approximate device location.';
  if (!Number.isInteger(data.focusMinutes) || data.focusMinutes < 1 || data.focusMinutes > 720)
    errors.focusMinutes = 'Must be a whole number between 1 and 720.';
  if (!Number.isInteger(data.breakMinutes) || data.breakMinutes < 0 || data.breakMinutes > 180)
    errors.breakMinutes = 'Must be a whole number between 0 and 180.';
  return errors;
}
