<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import TextInput from '../atoms/TextInput.svelte';
  import ToggleSwitch from '../atoms/ToggleSwitch.svelte';
  import { getSettingsState } from '../../model/SettingsState.svelte';

  const settingsState = getSettingsState();
</script>

<section class="panel notifications-panel" aria-labelledby="notifications-heading">
  <div class="panel-header">
    <AppIcon name="bell" scale={1.2} />
    <h3 id="notifications-heading">NOTIFICATIONS</h3>
  </div>
  
  <div class="panel-content">
    <TextInput
      id="milestoneReminderTime"
      label="Milestone reminder time"
      type="time"
      bind:value={settingsState.draftSettings.milestoneReminderTime}
      error={settingsState.validationErrors.milestoneReminderTime}
    />

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
    background: white;
    border: 1px solid #cfc9b9;
    border-radius: 8px;
    padding: 24px;
  }

  .panel-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
  }

  h3 {
    font-family: var(--bloom-title-font);
    font-size: 18px;
    color: var(--bloom-text-dark-blue);
    margin: 0;
  }

  .panel-content {
    display: flex;
    flex-direction: column;
  }

  .toggles {
    margin-top: 16px;
  }
</style>
