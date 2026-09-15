<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import SelectField from '../atoms/SelectField.svelte';
  import { getSettingsState } from '../../model/SettingsState.svelte';

  const settingsState = getSettingsState();

  const focusOptions = [5, 10, 15, 20, 25, 30, 45, 60].map(val => ({
    value: val,
    label: `${val} minutes`
  }));

  const breakOptions = [5, 10, 15, 20].map(val => ({
    value: val,
    label: `${val} minutes`
  }));
</script>

<section class="panel focus-panel" aria-labelledby="focus-heading">
  <div class="panel-header">
    <AppIcon name="clock" scale={1.2} />
    <h3 id="focus-heading">FOCUS TIMER</h3>
  </div>
  
  <div class="panel-content">
    <SelectField
      id="focusDuration"
      label="Focus duration"
      bind:value={settingsState.draftSettings.focusDurationMinutes}
      options={focusOptions}
      error={settingsState.validationErrors.focusDurationMinutes}
    />

    <SelectField
      id="breakDuration"
      label="Break duration"
      bind:value={settingsState.draftSettings.breakDurationMinutes}
      options={breakOptions}
      error={settingsState.validationErrors.breakDurationMinutes}
    />
  </div>
</section>

<style>
  .panel {
    background: var(--bloom-surface-cream-alt);
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 16px;
  }

  .panel-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
  }

  h3 {
    font-family: var(--bloom-display-font);
    font-size: 18px;
    color: var(--bloom-text-dark-blue);
    margin: 0;
  }

  .panel-content {
    display: flex;
    flex-direction: column;
  }
</style>
