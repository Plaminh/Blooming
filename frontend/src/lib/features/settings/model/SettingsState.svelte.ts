import { getContext, setContext } from "svelte";
import type { SettingsProfile } from "../types";
import { desktop } from "$lib/platform/desktopWindow";
import type { UserSettingsResponse } from "$lib/api/types";
import { get } from "svelte/store";
import { authStore } from "$lib/shared/stores/authStore";
import { deviceTimezone } from "$lib/shared/deviceLocation";
import { isValidTimezone, normalizeTimezone } from "$lib/shared/timezones";
import { authoritativeSettings, settingsResponseToProfile } from './userSettingsMapping';

export class SettingsState {
  savedSettings = $state<SettingsProfile>({
    email: "",
    timezone: deviceTimezone(),
    focusDurationMinutes: 25,
    breakDurationMinutes: 5,
    startAtLogin: true,
    keepWidgetOnTop: false,
    widgetVisibility: true,
    milestoneReminderLeadTimeMinutes: 1440,
    quietHoursEnabled: false,
    quietHoursStart: null,
    quietHoursEnd: null,
    weatherEnabled: false,
    weatherLocation: "",
    weatherLocationName: null,
    weatherLat: null,
    weatherLon: null,
    weatherAnimationEnabled: true,
  });

  draftSettings = $state<SettingsProfile>(
    JSON.parse(JSON.stringify(this.savedSettings)),
  );
  validationErrors = $state<Partial<Record<string, string>>>({});
  isSaving = $state(false);
  saveSuccessMessage = $state<string | null>(null);
  saveErrorMessage = $state<string | null>(null);
  syncWarning = $state<string | null>(null);
  locationPickerVersion = $state(0);

  isDirty = $derived(
    JSON.stringify(this.savedSettings) !== JSON.stringify(this.draftSettings),
  );

  constructor() {
    // Set initial email synchronously if available
    const user = get(authStore).user;
    if (user?.email) {
      this.savedSettings.email = user.email;
    }
    this.draftSettings = JSON.parse(JSON.stringify(this.savedSettings));

    const cached = get(authoritativeSettings);
    if (cached) {
      this.savedSettings = settingsResponseToProfile(cached, get(authStore).user?.email || '');
      this.draftSettings = JSON.parse(JSON.stringify(this.savedSettings));
    }

    this.loadFromAPI();
  }

  async loadFromAPI() {
    try {
      const { api } = await import("$lib/api");
      const stored: UserSettingsResponse | null = await api.get("/me/settings");
      if (stored) {
        authoritativeSettings.set(stored);
        this.savedSettings = settingsResponseToProfile(stored, get(authStore).user?.email || '');
        this.draftSettings = JSON.parse(JSON.stringify(this.savedSettings));
        try {
          await desktop.reconcileSettings(stored);
        } catch {
          this.syncWarning = "Settings loaded, but desktop sync failed.";
        }
      }
    } catch (e) {
      this.saveErrorMessage =
        e instanceof Error ? e.message : "Failed to load or apply settings.";
    }
  }

  validate(): boolean {
    this.validationErrors = {};
    let isValid = true;

    const {
      focusDurationMinutes,
      breakDurationMinutes,
      milestoneReminderLeadTimeMinutes,
      weatherLocation,
      timezone,
      quietHoursEnabled,
      quietHoursStart,
      quietHoursEnd,
    } = this.draftSettings;

    if (quietHoursEnabled) {
      if (!quietHoursStart || !quietHoursEnd) {
        this.validationErrors.quietHours = "Both start and end times are required when Quiet Hours are enabled.";
        isValid = false;
      }
    }

    if (!isValidTimezone(timezone)) {
      this.validationErrors.timezone = "Select a valid IANA timezone.";
      isValid = false;
    }

    if (focusDurationMinutes < 1 || focusDurationMinutes > 720) {
      this.validationErrors.focusDurationMinutes = "Must be between 1 and 720.";
      isValid = false;
    }

    if (breakDurationMinutes < 0 || breakDurationMinutes > 180) {
      this.validationErrors.breakDurationMinutes = "Must be between 0 and 180.";
      isValid = false;
    }

    if (
      !Number.isInteger(milestoneReminderLeadTimeMinutes) ||
      milestoneReminderLeadTimeMinutes < 0 ||
      milestoneReminderLeadTimeMinutes > 43200
    ) {
      this.validationErrors.milestoneReminderLeadTimeMinutes =
        "Must be a whole number between 0 and 43200.";
      isValid = false;
    }

    if (this.draftSettings.weatherEnabled) {
      if (
        this.draftSettings.weatherLat === null ||
        this.draftSettings.weatherLon === null ||
        !this.draftSettings.weatherLocationName?.trim()
      ) {
        this.validationErrors.weatherLocation = "Search and select a valid location to enable weather.";
        isValid = false;
      }
    }

    return isValid;
  }

  cancel() {
    this.draftSettings = JSON.parse(JSON.stringify(this.savedSettings));
    this.locationPickerVersion += 1;
    this.validationErrors = {};
    this.saveSuccessMessage = null;
    this.saveErrorMessage = null;
    this.syncWarning = null;
  }

  async save() {
    if (this.isSaving) return false;
    if (!this.validate()) return false;

    this.isSaving = true;
    this.saveSuccessMessage = null;
    this.saveErrorMessage = null;
    this.syncWarning = null;
    try {
      this.draftSettings.timezone = normalizeTimezone(this.draftSettings.timezone);

      const { api } = await import("$lib/api");

      const payload = {
        timezone: this.draftSettings.timezone,
        default_focus_minutes: Number(this.draftSettings.focusDurationMinutes),
        default_break_minutes: Number(this.draftSettings.breakDurationMinutes),
        launch_on_startup: this.draftSettings.startAtLogin,
        widget_always_on_top: this.draftSettings.keepWidgetOnTop,
        widget_visibility: this.draftSettings.widgetVisibility,
        milestone_reminder_lead_time_minutes: Number(
          this.draftSettings.milestoneReminderLeadTimeMinutes,
        ),
        quiet_hours_enabled: this.draftSettings.quietHoursEnabled,
        quiet_hours_start: this.draftSettings.quietHoursEnabled ? this.draftSettings.quietHoursStart : null,
        quiet_hours_end: this.draftSettings.quietHoursEnabled ? this.draftSettings.quietHoursEnd : null,
        weather_enabled: this.draftSettings.weatherEnabled,
        weather_location: this.draftSettings.weatherLocation.trim() || null,
        weather_location_name: this.draftSettings.weatherLocationName?.trim() || null,
        weather_lat: this.draftSettings.weatherLat,
        weather_lon: this.draftSettings.weatherLon,
        weather_animation_enabled: this.draftSettings.weatherAnimationEnabled,
      };

      const stored = await api.put("/me/settings", payload) as UserSettingsResponse;
      authoritativeSettings.set(stored);
      this.savedSettings = settingsResponseToProfile(stored, get(authStore).user?.email || '');
      this.draftSettings = JSON.parse(JSON.stringify(this.savedSettings));
      try {
        await desktop.reconcileSettings(stored);
      } catch {
        this.syncWarning = "Settings saved, but desktop settings could not be synchronized.";
      }
      this.saveSuccessMessage = "Settings saved successfully.";
      if (typeof window !== 'undefined') window.dispatchEvent(new Event('blooming:settings-updated'));
      try {
        await desktop.settingsUpdated();
      } catch {
        this.syncWarning = "Settings saved, but the widget could not refresh immediately.";
      }
      return true;
    } catch (e: unknown) {
      this.saveErrorMessage =
        e instanceof Error
          ? e.message
          : "Failed to save settings. Please try again.";
      return false;
    } finally {
      this.isSaving = false;
    }
  }

  logout() {
    authStore.clearAuth();
  }
}

const SETTINGS_CONTEXT_KEY = Symbol("SETTINGS_STATE");

export function setSettingsState() {
  const state = new SettingsState();
  setContext(SETTINGS_CONTEXT_KEY, state);
  return state;
}

export function getSettingsState() {
  return getContext<SettingsState>(SETTINGS_CONTEXT_KEY);
}
