<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import ToggleSwitch from '../atoms/ToggleSwitch.svelte';
  import WeatherLocationPicker from '../molecules/WeatherLocationPicker.svelte';
  import { getSettingsState } from '../../model/SettingsState.svelte';
  import TimezonePicker from '$lib/features/onboarding-setup/components/molecules/TimezonePicker.svelte';

  const settingsState = getSettingsState();

</script>

<section class="panel general-panel" aria-labelledby="general-heading">
  <div class="panel-header">
    <AppIcon name="settings" scale={1.2} />
    <h3 id="general-heading">GENERAL</h3>
  </div>
  
  <div class="panel-content">
    <div class="device-row">
      <span>Timezone</span>
      <div>
        <TimezonePicker id="settings-timezone" bind:value={settingsState.draftSettings.timezone} error={settingsState.validationErrors.timezone} />
        {#if settingsState.validationErrors.timezone}<span class="location-error" role="alert">{settingsState.validationErrors.timezone}</span>{/if}
      </div>
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
        initialValue={settingsState.draftSettings.weatherLocationName ?? ''}
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

    <div class="weather-toggles">
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
    box-sizing: border-box;
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
    gap: var(--space-3);
    margin-bottom: calc(var(--space-5) + var(--space-3));
    color: var(--bloom-text-dark-blue);
    font-family: var(--bloom-body-font);
    font-size: 16px;
    font-weight: 600;
  }


  .location-error { color: var(--bloom-error); }

  .settings-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    margin-bottom: calc(var(--space-5) + var(--space-3));
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

  .weather-toggles {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .weather-toggles :global(.toggle-group:last-child) {
    margin-bottom: 0;
  }

  @media (max-width: 760px) {
    .panel {
      height: auto;
    }
  }
</style>
