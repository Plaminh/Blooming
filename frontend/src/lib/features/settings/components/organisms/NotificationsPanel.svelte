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
    <SelectField
      id="milestoneReminderLeadTimeMinutes"
      label="Milestone reminder"
      bind:value={settingsState.draftSettings.milestoneReminderLeadTimeMinutes}
      options={reminderOptions}
      error={settingsState.validationErrors.milestoneReminderLeadTimeMinutes}
      layout="stacked"
    />
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
  }
</style>
