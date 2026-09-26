export interface SettingsProfile {
  email: string;
  timezone: string;
  focusDurationMinutes: number;
  breakDurationMinutes: number;
  startAtLogin: boolean;
  keepWidgetOnTop: boolean;
  milestoneReminderLeadTimeMinutes: number;
  weatherEnabled: boolean;
  weatherLocation: string;
  weatherLocationName: string | null;
  weatherLat: number | null;
  weatherLon: number | null;
  weatherAnimationEnabled: boolean;
}
