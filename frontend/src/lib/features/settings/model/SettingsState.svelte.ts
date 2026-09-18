import { getContext, setContext } from "svelte";
import type { SettingsProfile } from "../types";
import { desktop, type NativeSettings } from "$lib/platform/desktopWindow";
import type { UserSettingsResponse } from "$lib/api/types";
import { get } from "svelte/store";
import { authStore } from "$lib/shared/stores/authStore";

const SETTINGS_KEY = "bloom_settings";

export class SettingsState {
  savedSettings = $state<SettingsProfile>({
    email: "",
    mrBloomName: "Mr. Bloom",
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
    focusDurationMinutes: 25,
    breakDurationMinutes: 5,
    startAtLogin: true,
    keepWidgetOnTop: true,
    milestoneReminderLeadTimeMinutes: 1440,
    emailReminders: true,
    weatherEnabled: false,
    weatherLocation: "",
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

    // Load local desktop-only preferences first
    if (typeof localStorage !== "undefined") {
      const localPrefsStr = localStorage.getItem(SETTINGS_KEY);
      if (localPrefsStr) {
        try {
          const localPrefs = JSON.parse(localPrefsStr);
          if (typeof localPrefs.emailReminders === "boolean")
            this.savedSettings.emailReminders = localPrefs.emailReminders;
          this.draftSettings = JSON.parse(JSON.stringify(this.savedSettings));
        } catch (e) {
          // ignore parsing error
        }
      }
    }

    this.loadFromAPI();
  }

  async loadFromAPI() {
    try {
      const { api } = await import("$lib/api");
      const stored: UserSettingsResponse | null = await api.get("/me/settings");
      if (stored) {
        // Map backend schema to frontend schema if needed
        const mappedSettings = {
          email: get(authStore).user?.email || "",
          mrBloomName: stored.mr_bloom_display_name || "Mr. Bloom",
          timezone:
            stored.timezone ||
            Intl.DateTimeFormat().resolvedOptions().timeZone ||
            "UTC",
          focusDurationMinutes: stored.default_focus_minutes || 25,
          breakDurationMinutes: stored.default_break_minutes || 5,
          startAtLogin: stored.launch_on_startup ?? true,
          keepWidgetOnTop: stored.widget_always_on_top ?? true,
          milestoneReminderLeadTimeMinutes:
            stored.milestone_reminder_lead_time_minutes ?? 1440,
          emailReminders: this.savedSettings.emailReminders, // Keep local pref
          weatherEnabled: stored.weather_enabled ?? false,
          weatherLocation: stored.weather_location ?? "",
          weatherAnimationEnabled: stored.weather_animation_enabled ?? true,
        };
        this.savedSettings = { ...this.savedSettings, ...mappedSettings };
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
      mrBloomName,
      focusDurationMinutes,
      breakDurationMinutes,
      milestoneReminderLeadTimeMinutes,
      weatherLocation,
    } = this.draftSettings;

    if (!mrBloomName || mrBloomName.trim() === "") {
      this.validationErrors.mrBloomName = "Name cannot be empty.";
      isValid = false;
    } else if (mrBloomName.length > 60) {
      this.validationErrors.mrBloomName = "Name is too long.";
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

    if (weatherLocation.trim().length > 100 || (this.draftSettings.weatherEnabled && !weatherLocation.trim())) {
      this.validationErrors.weatherLocation = "Enter a location (up to 100 characters) to enable weather.";
      isValid = false;
    }

    return isValid;
  }

  cancel() {
    this.draftSettings = JSON.parse(JSON.stringify(this.savedSettings));
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
    let previousNativeSettings: NativeSettings | null = null;

    try {
      this.draftSettings.mrBloomName = this.draftSettings.mrBloomName.trim();

      const { api } = await import("$lib/api");

      const payload = {
        mr_bloom_display_name: this.draftSettings.mrBloomName,
        timezone: this.draftSettings.timezone,
        default_focus_minutes: Number(this.draftSettings.focusDurationMinutes),
        default_break_minutes: Number(this.draftSettings.breakDurationMinutes),
        launch_on_startup: this.draftSettings.startAtLogin,
        widget_always_on_top: this.draftSettings.keepWidgetOnTop,
        milestone_reminder_lead_time_minutes: Number(
          this.draftSettings.milestoneReminderLeadTimeMinutes,
        ),
        weather_enabled: this.draftSettings.weatherEnabled,
        weather_location: this.draftSettings.weatherLocation.trim() || null,
        weather_animation_enabled: this.draftSettings.weatherAnimationEnabled,
      };

      previousNativeSettings = await desktop.readSettings();
      try {
        await desktop.reconcileSettings(payload);
        await api.put("/me/settings", payload);
      } catch (error) {
        if (previousNativeSettings) {
          try {
            await desktop.reconcileSettings(previousNativeSettings);
          } catch {
            this.syncWarning =
              "Previous desktop settings could not be restored. Reopen Settings to synchronize.";
          }
        }
        throw error;
      }
      this.savedSettings = JSON.parse(JSON.stringify(this.draftSettings));
      this.saveSuccessMessage = "Settings saved successfully.";
      try {
        await desktop.settingsUpdated();
      } catch {
        this.syncWarning = "Settings saved, but the widget could not refresh immediately.";
      }
      try {
        if (typeof localStorage !== "undefined") {
          localStorage.setItem(
            SETTINGS_KEY,
            JSON.stringify({
              emailReminders: this.savedSettings.emailReminders,
            }),
          );
        }
      } catch {
        this.syncWarning =
          "Settings saved, but local preferences could not be stored.";
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
