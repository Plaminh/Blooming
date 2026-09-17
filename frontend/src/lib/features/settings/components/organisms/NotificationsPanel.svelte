<script lang="ts">
  import AppIcon from "$lib/shared/components/atoms/AppIcon.svelte";
  import ToggleSwitch from "../atoms/ToggleSwitch.svelte";
  import { getSettingsState } from "../../model/SettingsState.svelte";

  const settingsState = getSettingsState();
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
    <label for="milestoneReminderLeadTimeMinutes">Milestone reminder</label>
    <select
      id="milestoneReminderLeadTimeMinutes"
      bind:value={settingsState.draftSettings.milestoneReminderLeadTimeMinutes}
    >
      <option value={0}>At the deadline</option>
      <option value={60}>One hour before</option>
      <option value={1440}>One day before</option>
      <option value={4320}>Three days before</option>
      {#if ![0, 60, 1440, 4320].includes(settingsState.draftSettings.milestoneReminderLeadTimeMinutes)}
        <option
          value={settingsState.draftSettings.milestoneReminderLeadTimeMinutes}
          >{settingsState.draftSettings.milestoneReminderLeadTimeMinutes} minutes
          before</option
        >
      {/if}
    </select>
    {#if settingsState.validationErrors.milestoneReminderLeadTimeMinutes}
      <p role="alert">
        {settingsState.validationErrors.milestoneReminderLeadTimeMinutes}
      </p>
    {/if}

    <div class="toggles">
      <ToggleSwitch
        id="emailReminders"
        label="Email reminders"
        bind:checked={settingsState.draftSettings.emailReminders}
      />
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
  }

  .toggles {
    margin-top: 8px;
  }
</style>
