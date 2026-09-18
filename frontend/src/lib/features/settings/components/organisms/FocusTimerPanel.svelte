<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import FocusTimerFields from '../molecules/FocusTimerFields.svelte';
  import { getSettingsState } from '../../model/SettingsState.svelte';

  const settingsState = getSettingsState();
</script>

<section class="panel focus-panel" aria-labelledby="focus-heading">
  <div class="panel-header">
    <AppIcon name="clock" scale={1.2} />
    <h3 id="focus-heading">FOCUS TIMER</h3>
  </div>
  
  <div class="panel-content">
    <FocusTimerFields
      bind:focusMinutes={settingsState.draftSettings.focusDurationMinutes}
      bind:breakMinutes={settingsState.draftSettings.breakDurationMinutes}
      focusError={settingsState.validationErrors.focusDurationMinutes}
      breakError={settingsState.validationErrors.breakDurationMinutes}
    />
  </div>
</section>

<style>
  .panel {
    background: var(--bloom-settings-panel-bg);
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
