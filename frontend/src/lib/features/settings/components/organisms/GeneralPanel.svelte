<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import TextInput from '$lib/shared/components/atoms/TextInput.svelte';
  import ToggleSwitch from '../atoms/ToggleSwitch.svelte';
  import WeatherLocationPicker from '../molecules/WeatherLocationPicker.svelte';
  import { getSettingsState } from '../../model/SettingsState.svelte';
  import { deviceTimezone } from '$lib/shared/deviceLocation';

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

    <div class="settings-group">
      <span class="group-label">Weather Location</span>
      {#if settingsState.savedSettings.weatherLocationName}
        <div class="current-location">
          Saved: <strong>{settingsState.savedSettings.weatherLocationName}</strong>
        </div>
      {:else if settingsState.savedSettings.weatherLocation}
        <span role="status">Confirm your weather location by selecting a place.</span>
      {/if}
      {#key settingsState.locationPickerVersion}
      <WeatherLocationPicker
        onInvalidate={() => {
          settingsState.draftSettings.weatherLocationName = null;
          settingsState.draftSettings.weatherLat = null;
          settingsState.draftSettings.weatherLon = null;
        }}
        onSelect={(place) => {
          settingsState.draftSettings.weatherLocationName = place.locationName;
          settingsState.draftSettings.weatherLat = place.lat;
          settingsState.draftSettings.weatherLon = place.lon;
          // Clear error if any
          delete settingsState.validationErrors.weatherLocation;
        }} 
      />
      {/key}
      {#if settingsState.validationErrors.weatherLocation}
        <span class="location-error" role="alert">{settingsState.validationErrors.weatherLocation}</span>
      {/if}
    </div>

    <div class="settings-group" style="margin-top: 12px; margin-bottom: 12px;">
      <label class="group-label" for="sceneSeason">Garden Season Override</label>
      <select 
        id="sceneSeason"
        bind:value={settingsState.draftSettings.sceneSeason}
        class="season-select"
      >
        <option value="AUTO">Auto (Based on weather/date)</option>
        <option value="SPRING">Spring</option>
        <option value="SUMMER">Summer</option>
        <option value="AUTUMN">Autumn</option>
        <option value="WINTER">Winter</option>
      </select>
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

  .location-error { color: var(--bloom-error); }

  .toggles {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .settings-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .group-label {
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 600;
    color: var(--bloom-text-dark-blue);
  }
  .current-location {
    font-size: 14px;
    color: var(--bloom-text-dark-blue);
  }
  .season-select {
    padding: 8px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 4px;
    background: var(--bloom-surface-cream-alt);
    font-family: var(--bloom-body-font);
    font-size: 14px;
  }
</style>
