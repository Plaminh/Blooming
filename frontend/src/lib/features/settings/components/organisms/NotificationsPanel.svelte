<script lang="ts">
  import AppIcon from "$lib/shared/components/atoms/AppIcon.svelte";
  import SelectField from "../atoms/SelectField.svelte";
  import { getSettingsState } from "../../model/SettingsState.svelte";

  const settingsState = getSettingsState();
  const reminderOptions = $derived([
    { value: 0, label: 'At the deadline' },
    { value: 60, label: 'One hour before' },
    { value: 1440, label: 'One day before' },
    { value: 4320, label: 'Three days before' },
    ...(![0, 60, 1440, 4320].includes(settingsState.draftSettings.milestoneReminderLeadTimeMinutes)
      ? [{
          value: settingsState.draftSettings.milestoneReminderLeadTimeMinutes,
          label: `${settingsState.draftSettings.milestoneReminderLeadTimeMinutes} minutes before`,
        }]
      : []),
  ]);
</script>

<section
  class="panel notifications-panel"
  aria-labelledby="notifications-heading"
>
  <div class="panel-header">
    <AppIcon name="bell" scale={1.2} />
    <h3 id="notifications-heading">NOTIFICATIONS</h3>
  </div>

  <div class="panel-content">
    <div class="setting-row">
      <SelectField
        id="milestoneReminderLeadTimeMinutes"
        label="Milestone reminder"
        bind:value={settingsState.draftSettings.milestoneReminderLeadTimeMinutes}
        options={reminderOptions}
        error={settingsState.validationErrors.milestoneReminderLeadTimeMinutes}
        layout="stacked"
      />
    </div>

    <div class="setting-row toggle-row">
      <div class="toggle-container">
        <label for="quietHoursEnabled" class="toggle-label">Enable Quiet Hours</label>
        <input type="checkbox" id="quietHoursEnabled" bind:checked={settingsState.draftSettings.quietHoursEnabled} />
      </div>
      {#if settingsState.draftSettings.quietHoursEnabled}
        <div class="time-inputs">
          <div class="time-field">
            <label for="quietHoursStart">Start Time</label>
            <input type="time" id="quietHoursStart" bind:value={settingsState.draftSettings.quietHoursStart} />
          </div>
          <div class="time-field">
            <label for="quietHoursEnd">End Time</label>
            <input type="time" id="quietHoursEnd" bind:value={settingsState.draftSettings.quietHoursEnd} />
          </div>
        </div>
      {/if}
      {#if settingsState.validationErrors.quietHours}
        <span class="error" role="alert">{settingsState.validationErrors.quietHours}</span>
      {/if}
    </div>
  </div>
</section>

<style>
  .panel {
    background: var(--bloom-settings-panel-bg);
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 8px;
    padding: 18px;
  }

  .panel-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
  }

  h3 {
    font-family: var(--bloom-display-font);
    font-size: var(--bloom-panel-title-size);
    font-weight: var(--bloom-panel-title-weight);
    letter-spacing: var(--bloom-panel-title-tracking);
    line-height: var(--bloom-panel-title-line-height);
    color: var(--bloom-text-dark-blue);
    margin: 0;
  }

  .panel-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .setting-row {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .toggle-container {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .toggle-label {
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 600;
    color: var(--bloom-text-dark-blue);
  }
  .time-inputs {
    display: flex;
    gap: 16px;
  }
  .time-field {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .time-field label {
    font-family: var(--bloom-body-font);
    font-size: 12px;
    color: var(--bloom-text-dark-blue);
  }
  .time-field input {
    padding: 6px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 4px;
  }
  .error { color: var(--bloom-error); font-size: 12px; }
</style>
