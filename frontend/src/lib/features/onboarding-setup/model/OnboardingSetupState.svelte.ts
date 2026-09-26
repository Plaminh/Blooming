import { deviceTimezone } from '$lib/shared/deviceLocation';
import { normalizeTimezone } from '$lib/shared/timezones';

export type FocusPreset = '25 / 5' | '50 / 10' | 'CUSTOM';

export interface OnboardingSetupData {
  timezone: string;
  focusPreset: FocusPreset;
  focusMinutes: number;
  breakMinutes: number;
  startAtLogin: boolean;
  keepWidgetOnTop: boolean;
  weatherLocation: string;
  weatherLocationName: string | null;
  weatherLat: number | null;
  weatherLon: number | null;
}

export class OnboardingSetupState {
  timezone = $state(normalizeTimezone(deviceTimezone()));
  focusPreset = $state<FocusPreset>('25 / 5');
  focusMinutes = $state(25);
  breakMinutes = $state(5);
  startAtLogin = $state(true);
  keepWidgetOnTop = $state(true);
  weatherLocation = $state('');
  weatherLocationName = $state<string | null>(null);
  weatherLat = $state<number | null>(null);
  weatherLon = $state<number | null>(null);

  constructor(initialData?: Partial<OnboardingSetupData>) {
    if (initialData) {
      if (initialData.timezone !== undefined) this.timezone = normalizeTimezone(initialData.timezone);
      if (initialData.focusPreset !== undefined) this.focusPreset = initialData.focusPreset;
      if (initialData.focusMinutes !== undefined) this.focusMinutes = initialData.focusMinutes;
      if (initialData.breakMinutes !== undefined) this.breakMinutes = initialData.breakMinutes;
      if (initialData.startAtLogin !== undefined) this.startAtLogin = initialData.startAtLogin;
      if (initialData.keepWidgetOnTop !== undefined) this.keepWidgetOnTop = initialData.keepWidgetOnTop;
      if (initialData.weatherLocation !== undefined) this.weatherLocation = initialData.weatherLocation;
      if (initialData.weatherLocationName !== undefined) this.weatherLocationName = initialData.weatherLocationName;
      if (initialData.weatherLat !== undefined) this.weatherLat = initialData.weatherLat;
      if (initialData.weatherLon !== undefined) this.weatherLon = initialData.weatherLon;
    }
  }

  get data(): OnboardingSetupData {
    return {
      timezone: this.timezone,
      focusPreset: this.focusPreset,
      focusMinutes: this.focusPreset === '25 / 5' ? 25 : this.focusPreset === '50 / 10' ? 50 : Number(this.focusMinutes),
      breakMinutes: this.focusPreset === '25 / 5' ? 5 : this.focusPreset === '50 / 10' ? 10 : Number(this.breakMinutes),
      startAtLogin: this.startAtLogin,
      keepWidgetOnTop: this.keepWidgetOnTop,
      weatherLocation: this.weatherLocation,
      weatherLocationName: this.weatherLocationName,
      weatherLat: this.weatherLat,
      weatherLon: this.weatherLon,
    };
  }
}
