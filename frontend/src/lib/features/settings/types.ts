export interface SettingsProfile {
  email: string;
  timezone: string;
  focusDurationMinutes: number;
  breakDurationMinutes: number;
  startAtLogin: boolean;
  keepWidgetOnTop: boolean;
  widgetVisibility: boolean;
  milestoneReminderLeadTimeMinutes: number;
  quietHoursEnabled: boolean;
  quietHoursStart: string | null;
  quietHoursEnd: string | null;
  weatherEnabled: boolean;
  weatherLocation: string;
  weatherLocationName: string | null;
  weatherLat: number | null;
  weatherLon: number | null;
  weatherAnimationEnabled: boolean;
}
