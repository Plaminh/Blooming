import { getContext, setContext } from 'svelte';
import type { SettingsProfile } from '../types';
import { Window } from '@tauri-apps/api/window';
import { goto } from '$app/navigation';

const SETTINGS_KEY = 'bloom_settings';

export class SettingsState {
  savedSettings = $state<SettingsProfile>({
    email: 'you@example.com',
    mrBloomName: 'Mr. Bloom',
    timezone: 'Asia/Ho_Chi_Minh',
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

  isDirty = $derived(JSON.stringify(this.savedSettings) !== JSON.stringify(this.draftSettings));

  constructor() {
    this.loadFromAPI();
  }

  async loadFromAPI() {
    try {
      const { api } = await import('$lib/api');
      const stored = await api.get('/api/v1/me/settings');
      if (stored) {
        // Map backend schema to frontend schema if needed
        const mappedSettings = {
          email: 'you@example.com', // get from user info?
          mrBloomName: stored.mr_bloom_name || 'Mr. Bloom',
          timezone: stored.timezone || 'Asia/Ho_Chi_Minh',
          focusDurationMinutes: stored.focus_duration_minutes || 25,
          breakDurationMinutes: stored.break_duration_minutes || 5,
          startAtLogin: stored.start_at_login ?? true,
          keepWidgetOnTop: stored.keep_widget_on_top ?? true,
          milestoneReminderTime: stored.milestone_reminder_time || '20:00',
          emailReminders: stored.email_reminders ?? true
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
    } else if (mrBloomName.length > 50) {
      this.validationErrors.mrBloomName = "Name is too long.";
      isValid = false;
    }

    if (focusDurationMinutes <= 0) {
      this.validationErrors.focusDurationMinutes = "Must be greater than 0.";
      isValid = false;
    }

    if (breakDurationMinutes <= 0) {
      this.validationErrors.breakDurationMinutes = "Must be greater than 0.";
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
  }

  async save() {
    if (this.isSaving) return false;
    if (!this.validate()) return false;

    this.isSaving = true;
    this.saveSuccessMessage = null;

    try {
      this.draftSettings.mrBloomName = this.draftSettings.mrBloomName.trim();

      const { api } = await import('$lib/api');
      
      const payload = {
        mr_bloom_name: this.draftSettings.mrBloomName,
        timezone: this.draftSettings.timezone,
        focus_duration_minutes: this.draftSettings.focusDurationMinutes,
        break_duration_minutes: this.draftSettings.breakDurationMinutes,
        start_at_login: this.draftSettings.startAtLogin,
        keep_widget_on_top: this.draftSettings.keepWidgetOnTop,
        milestone_reminder_time: this.draftSettings.milestoneReminderTime,
        email_reminders: this.draftSettings.emailReminders
      };
      
      await api.put('/api/v1/me/settings', payload);

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

      this.saveSuccessMessage = "Settings saved successfully.";
      return true;
    } catch (e) {
      console.error('Failed to save settings via API', e);
      return false;
    } finally {
      this.isSaving = false;
      setTimeout(() => {
        if (this.saveSuccessMessage) this.saveSuccessMessage = null;
      }, 3000);
    }
  }

  logout() {
    import('$lib/shared/stores/authStore').then(({ authStore }) => {
      authStore.clearAuth();
    });
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
