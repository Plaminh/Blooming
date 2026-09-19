<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import TextInput from '$lib/shared/components/atoms/TextInput.svelte';
  import ToggleSwitch from '../atoms/ToggleSwitch.svelte';
  import { getSettingsState } from '../../model/SettingsState.svelte';
  import { deviceTimezone, isDeviceCoordinates } from '$lib/shared/deviceLocation';

  const settingsState = getSettingsState();

</script>

<section class="panel general-panel" aria-labelledby="general-heading">
  <div class="panel-header">
    <AppIcon name="settings" scale={1.2} />
    <h3 id="general-heading">GENERAL</h3>
  </div>
  
  <div class="panel-content">
    <TextInput
      id="mrBloomName"
      label="Mr. Bloom's name"
      bind:value={settingsState.draftSettings.mrBloomName}
      error={settingsState.validationErrors.mrBloomName}
    />

    <div class="device-row">
      <span>Timezone</span>
      <output aria-label="Device timezone">{deviceTimezone()}</output>
    </div>

    <TextInput
      id="weatherLocation"
      label="Weather location"
      bind:value={settingsState.draftSettings.weatherLocation}
      error={settingsState.validationErrors.weatherLocation}
    />
    <div class="location-action">
      <button type="button" disabled={settingsState.locationPending} onclick={() => settingsState.useDeviceLocation()}>
        {settingsState.locationPending ? 'Finding location...' : 'Use device location'}
      </button>
      {#if isDeviceCoordinates(settingsState.draftSettings.weatherLocation)}
        <span role="status">Device location selected</span>
      {/if}
      {#if settingsState.locationError}
        <span class="location-error" role="alert">{settingsState.locationError}</span>
      {/if}
    </div>

    <ToggleSwitch
      id="weatherEnabled"
      label="Show local weather in widget"
      bind:checked={settingsState.draftSettings.weatherEnabled}
    />

    <ToggleSwitch
      id="weatherAnimationEnabled"
      label="Animate rain in widget"
      bind:checked={settingsState.draftSettings.weatherAnimationEnabled}
    />

    <div class="toggles">
      <ToggleSwitch
        id="startAtLogin"
        label="Start Blooming at login"
        bind:checked={settingsState.draftSettings.startAtLogin}
      />

      <ToggleSwitch
        id="keepWidgetOnTop"
        label="Keep widget on top"
        bind:checked={settingsState.draftSettings.keepWidgetOnTop}
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
    margin-bottom: 16px;
    height: 100%;
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

  .device-row {
    display: grid;
    grid-template-columns: 220px minmax(0, 1fr);
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
    color: var(--bloom-text-dark-blue);
    font-family: var(--bloom-body-font);
    font-size: 16px;
    font-weight: 600;
  }

  .device-row output {
    padding: 10px 14px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 4px;
    background: var(--bloom-surface-cream-alt);
    font-weight: 400;
  }

  .location-action {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin: -6px 0 14px 232px;
    font: 14px var(--bloom-body-font);
  }

  .location-action button {
    padding: 7px 10px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 4px;
    background: var(--bloom-surface-cream-alt);
    color: var(--bloom-text-dark-blue);
    cursor: pointer;
  }

  .location-error { color: var(--bloom-error); }

  .toggles {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
</style>
