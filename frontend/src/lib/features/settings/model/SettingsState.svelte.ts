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
    this.loadFromStorage();
  }

  loadFromStorage() {
    if (typeof localStorage !== 'undefined') {
      const stored = localStorage.getItem(SETTINGS_KEY);
      if (stored) {
        try {
          this.savedSettings = { ...this.savedSettings, ...JSON.parse(stored) };
          this.draftSettings = JSON.parse(JSON.stringify(this.savedSettings));
        } catch (e) {
          console.error('Failed to parse settings from local storage', e);
        }
      }
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
      // Trim name before saving
      this.draftSettings.mrBloomName = this.draftSettings.mrBloomName.trim();

      // Mock Local Persistence
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(SETTINGS_KEY, JSON.stringify(this.draftSettings));
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

      this.saveSuccessMessage = "Settings saved successfully.";
      return true;
    } finally {
      this.isSaving = false;
      setTimeout(() => {
        if (this.saveSuccessMessage) this.saveSuccessMessage = null;
      }, 3000);
    }
  }

  logout() {
    // Local mock logout handler
    void goto('/auth');
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
