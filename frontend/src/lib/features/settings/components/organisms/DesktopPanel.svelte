<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import ToggleSwitch from '../atoms/ToggleSwitch.svelte';
  import { getSettingsState } from '../../model/SettingsState.svelte';

  const settingsState = getSettingsState();
</script>

<section class="panel desktop-panel" aria-labelledby="desktop-heading">
  <div class="panel-header">
    <AppIcon name="settings" scale={1.2} />
    <h3 id="desktop-heading">DESKTOP</h3>
  </div>

  <div class="panel-content">
    <ToggleSwitch
      id="startAtLogin"
      label="Start Blooming at login"
      bind:checked={settingsState.draftSettings.startAtLogin}
    />
    <ToggleSwitch
      id="widgetVisibility"
      label="Show companion widget"
      bind:checked={settingsState.draftSettings.widgetVisibility}
    />
    <ToggleSwitch
      id="keepWidgetOnTop"
      label="Keep widget on top"
      bind:checked={settingsState.draftSettings.keepWidgetOnTop}
    />
  </div>
</section>

<style>
  .panel {
    background: var(--bloom-settings-panel-bg);
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 8px;
    padding: 18px;
    margin-top: 16px;
  }

  .panel-header, .panel-content {
    display: flex;
  }

  .panel-header {
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
  }

  .panel-content {
    flex-direction: column;
    gap: 12px;
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
</style>
