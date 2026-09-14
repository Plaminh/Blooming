import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SettingsState } from './SettingsState.svelte';

describe('SettingsState', () => {
  let state: SettingsState;

  beforeEach(() => {
    localStorage.clear();
    state = new SettingsState();
  });

  it('initializes with default fixture values', () => {
    expect(state.savedSettings.email).toBe('you@example.com');
    expect(state.savedSettings.mrBloomName).toBe('Mr. Bloom');
    expect(state.savedSettings.timezone).toBe('Asia/Ho_Chi_Minh');
    expect(state.savedSettings.focusDurationMinutes).toBe(25);
    expect(state.savedSettings.breakDurationMinutes).toBe(5);
    expect(state.savedSettings.startAtLogin).toBe(true);
    expect(state.savedSettings.keepWidgetOnTop).toBe(true);
    expect(state.savedSettings.milestoneReminderTime).toBe('20:00');
    expect(state.savedSettings.emailReminders).toBe(true);
  });

  it('calculates dirty state correctly', () => {
    expect(state.isDirty).toBe(false);
    
    state.draftSettings.mrBloomName = 'New Name';
    expect(state.isDirty).toBe(true);
    
    state.draftSettings.mrBloomName = 'Mr. Bloom';
    expect(state.isDirty).toBe(false);
  });

  it('cancels changes by reverting draft to saved', () => {
    state.draftSettings.mrBloomName = 'Discarded Name';
    state.cancel();
    expect(state.draftSettings.mrBloomName).toBe('Mr. Bloom');
    expect(state.isDirty).toBe(false);
  });

  it('validates name length and emptiness', () => {
    state.draftSettings.mrBloomName = '   ';
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.mrBloomName).toBeDefined();

    state.draftSettings.mrBloomName = 'A'.repeat(51);
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.mrBloomName).toBeDefined();

    state.draftSettings.mrBloomName = 'Valid Name';
    expect(state.validate()).toBe(true);
  });

  it('validates duration bounds', () => {
    state.draftSettings.focusDurationMinutes = 0;
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.focusDurationMinutes).toBeDefined();

    state.draftSettings.focusDurationMinutes = 25;
    state.draftSettings.breakDurationMinutes = -5;
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.breakDurationMinutes).toBeDefined();
  });

  it('validates time format', () => {
    state.draftSettings.milestoneReminderTime = 'invalid';
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.milestoneReminderTime).toBeDefined();

    state.draftSettings.milestoneReminderTime = '25:00';
    expect(state.validate()).toBe(false);
    expect(state.validationErrors.milestoneReminderTime).toBeDefined();

    state.draftSettings.milestoneReminderTime = '12:30';
    expect(state.validate()).toBe(true);
  });

  it('saves successfully', async () => {
    state.draftSettings.mrBloomName = 'Saved Name';
    const success = await state.save();
    
    expect(success).toBe(true);
    expect(state.savedSettings.mrBloomName).toBe('Saved Name');
    expect(state.isDirty).toBe(false);
    expect(localStorage.getItem('bloom_settings')).toContain('Saved Name');
  });
});
