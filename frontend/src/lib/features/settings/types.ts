export interface SettingsProfile {
  email: string;
  mrBloomName: string;
  timezone: string;
  focusDurationMinutes: number;
  breakDurationMinutes: number;
  startAtLogin: boolean;
  keepWidgetOnTop: boolean;
  milestoneReminderLeadTimeMinutes: number;
  emailReminders: boolean;
  weatherEnabled: boolean;
  weatherLocation: string;
  weatherLocationName: string | null;
  weatherLat: number | null;
  weatherLon: number | null;
  sceneSeason: string;
  weatherAnimationEnabled: boolean;
}
