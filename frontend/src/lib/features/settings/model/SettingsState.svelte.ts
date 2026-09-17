import { getContext, setContext } from 'svelte';
import type { SettingsProfile } from '../types';
import { Window } from '@tauri-apps/api/window';
import { get } from 'svelte/store';
import { authStore } from '$lib/shared/stores/authStore';

const SETTINGS_KEY = 'bloom_settings';

export class SettingsState {
  savedSettings = $state<SettingsProfile>({
    email: '',
    mrBloomName: 'Mr. Bloom',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
    focusDurationMinutes: 25,
    breakDurationMinutes: 5,
    startAtLogin: true,
    keepWidgetOnTop: true,
    milestoneReminderTime: '20:00',
    emailReminders: true
  });

  draftSettings = $state<SettingsProfile>(JSON.parse(JSON.stringify(this.savedSettings)));
  validationErrors = $state<Partial<Record<keyof SettingsProfile, string>>>({});
  isSaving = $state(false);
  saveSuccessMessage = $state<string | null>(null);
  saveErrorMessage = $state<string | null>(null);

  isDirty = $derived(JSON.stringify(this.savedSettings) !== JSON.stringify(this.draftSettings));

  constructor() {
    // Set initial email synchronously if available
    const user = get(authStore).user;
    if (user?.email) {
      this.savedSettings.email = user.email;
    }
    this.draftSettings = JSON.parse(JSON.stringify(this.savedSettings));
    
    // Load local desktop-only preferences first
    if (typeof localStorage !== 'undefined') {
      const localPrefsStr = localStorage.getItem(SETTINGS_KEY);
      if (localPrefsStr) {
        try {
          const localPrefs = JSON.parse(localPrefsStr);
          if (localPrefs.milestoneReminderTime) this.savedSettings.milestoneReminderTime = localPrefs.milestoneReminderTime;
          if (typeof localPrefs.emailReminders === 'boolean') this.savedSettings.emailReminders = localPrefs.emailReminders;
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
      const { api } = await import('$lib/api');
      const stored = await api.get('/me/settings');
      if (stored) {
        // Map backend schema to frontend schema if needed
        const mappedSettings = {
          email: get(authStore).user?.email || '',
          mrBloomName: stored.mr_bloom_display_name || 'Mr. Bloom',
          timezone: stored.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
          focusDurationMinutes: stored.default_focus_minutes || 25,
          breakDurationMinutes: stored.default_break_minutes || 5,
          startAtLogin: stored.launch_on_startup ?? true,
          keepWidgetOnTop: stored.widget_always_on_top ?? true,
          milestoneReminderTime: this.savedSettings.milestoneReminderTime, // Keep local pref
          emailReminders: this.savedSettings.emailReminders // Keep local pref
        };
        this.savedSettings = { ...this.savedSettings, ...mappedSettings };
        this.draftSettings = JSON.parse(JSON.stringify(this.savedSettings));
      }
    } catch (e) {
      console.error('Failed to load settings from API', e);
    }
  }

  validate(): boolean {
    this.validationErrors = {};
    let isValid = true;

    const { mrBloomName, focusDurationMinutes, breakDurationMinutes, milestoneReminderTime } = this.draftSettings;

    if (!mrBloomName || mrBloomName.trim() === '') {
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

    const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)$/;
    if (!timeRegex.test(milestoneReminderTime)) {
      this.validationErrors.milestoneReminderTime = "Invalid time format.";
      isValid = false;
    }

    return isValid;
  }

  cancel() {
    this.draftSettings = JSON.parse(JSON.stringify(this.savedSettings));
    this.validationErrors = {};
    this.saveSuccessMessage = null;
    this.saveErrorMessage = null;
  }

  async save() {
    if (this.isSaving) return false;
    if (!this.validate()) return false;

    this.isSaving = true;
    this.saveSuccessMessage = null;
    this.saveErrorMessage = null;

    try {
      this.draftSettings.mrBloomName = this.draftSettings.mrBloomName.trim();

      const { api } = await import('$lib/api');
      
      const payload = {
        mr_bloom_display_name: this.draftSettings.mrBloomName,
        timezone: this.draftSettings.timezone,
        default_focus_minutes: this.draftSettings.focusDurationMinutes,
        default_break_minutes: this.draftSettings.breakDurationMinutes,
        launch_on_startup: this.draftSettings.startAtLogin,
        widget_always_on_top: this.draftSettings.keepWidgetOnTop
      };
      
      await api.put('/me/settings', payload);
      
      // Save desktop-only preferences locally
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(SETTINGS_KEY, JSON.stringify({
          milestoneReminderTime: this.draftSettings.milestoneReminderTime,
          emailReminders: this.draftSettings.emailReminders
        }));
      }

      this.savedSettings = JSON.parse(JSON.stringify(this.draftSettings));

      // Tauri API integration for Keep widget on top
      try {
        const widgetWindow = await Window.getByLabel('companion-widget');
        if (widgetWindow) {
          await widgetWindow.setAlwaysOnTop(this.savedSettings.keepWidgetOnTop);
        }
      } catch (err) {
        console.warn('Failed to apply always-on-top setting, browser fallback used:', err);
      }

      // Update the user display name in authStore (matches User schema now, though mr_bloom_display_name is in settings, user has display_name. Wait, user has display_name, not mr_bloom_display_name.)
      // We'll leave it out since mr_bloom_display_name is part of settings, not the auth user schema.
      // Removed authStore.updateUser as it does not belong to the user schema.

      this.saveSuccessMessage = "Settings saved successfully.";
      return true;
    } catch (e: any) {
      console.error('Failed to save settings via API', e);
      this.saveErrorMessage = e.message || 'Failed to save settings. Please try again.';
      return false;
    } finally {
      this.isSaving = false;
    }
  }

  logout() {
    authStore.clearAuth();
  }
}

const SETTINGS_CONTEXT_KEY = Symbol('SETTINGS_STATE');

export function setSettingsState() {
  const state = new SettingsState();
  setContext(SETTINGS_CONTEXT_KEY, state);
  return state;
}

export function getSettingsState() {
  return getContext<SettingsState>(SETTINGS_CONTEXT_KEY);
}
