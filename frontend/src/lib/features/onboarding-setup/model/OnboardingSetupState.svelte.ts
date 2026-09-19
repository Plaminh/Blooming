import { deviceTimezone } from '$lib/shared/deviceLocation';

export type FocusPreset = '25 / 5' | '50 / 10' | 'CUSTOM';

export interface OnboardingSetupData {
  name: string;
  timezone: string;
  focusPreset: FocusPreset;
  startAtLogin: boolean;
  keepWidgetOnTop: boolean;
  weatherLocation: string;
}

export class OnboardingSetupState {
  name = $state('Mr. Bloom');
  timezone = $state(deviceTimezone());
  focusPreset = $state<FocusPreset>('25 / 5');
  startAtLogin = $state(true);
  keepWidgetOnTop = $state(true);
  weatherLocation = $state('');

  constructor(initialData?: Partial<OnboardingSetupData>) {
    if (initialData) {
      if (initialData.name !== undefined) this.name = initialData.name;
      if (initialData.timezone !== undefined) this.timezone = initialData.timezone;
      if (initialData.focusPreset !== undefined) this.focusPreset = initialData.focusPreset;
      if (initialData.startAtLogin !== undefined) this.startAtLogin = initialData.startAtLogin;
      if (initialData.keepWidgetOnTop !== undefined) this.keepWidgetOnTop = initialData.keepWidgetOnTop;
      if (initialData.weatherLocation !== undefined) this.weatherLocation = initialData.weatherLocation;
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
    };
  }
}
