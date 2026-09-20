import { deviceTimezone } from '$lib/shared/deviceLocation';

export type FocusPreset = '25 / 5' | '50 / 10' | 'CUSTOM';

export interface OnboardingSetupData {
  name: string;
  timezone: string;
  focusPreset: FocusPreset;
  startAtLogin: boolean;
  keepWidgetOnTop: boolean;
  weatherLocation: string;
  weatherLocationName: string | null;
  weatherLat: number | null;
  weatherLon: number | null;
}

export class OnboardingSetupState {
  name = $state('Mr. Bloom');
  timezone = $state(deviceTimezone());
  focusPreset = $state<FocusPreset>('25 / 5');
  startAtLogin = $state(true);
  keepWidgetOnTop = $state(true);
  weatherLocation = $state('');
  weatherLocationName = $state<string | null>(null);
  weatherLat = $state<number | null>(null);
  weatherLon = $state<number | null>(null);

  constructor(initialData?: Partial<OnboardingSetupData>) {
    if (initialData) {
      if (initialData.name !== undefined) this.name = initialData.name;
      if (initialData.timezone !== undefined) this.timezone = initialData.timezone;
      if (initialData.focusPreset !== undefined) this.focusPreset = initialData.focusPreset;
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
      name: this.name,
      timezone: this.timezone,
      focusPreset: this.focusPreset,
      startAtLogin: this.startAtLogin,
      keepWidgetOnTop: this.keepWidgetOnTop,
      weatherLocation: this.weatherLocation,
      weatherLocationName: this.weatherLocationName,
      weatherLat: this.weatherLat,
      weatherLon: this.weatherLon,
    };
  }
}
