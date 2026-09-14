<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import TextInput from '../atoms/TextInput.svelte';
  import SelectField from '../atoms/SelectField.svelte';
  import ToggleSwitch from '../atoms/ToggleSwitch.svelte';
  import { getSettingsState } from '../../model/SettingsState.svelte';

  const settingsState = getSettingsState();

  const timezoneOptions = Intl.supportedValuesOf('timeZone').map(tz => ({
    value: tz,
    label: tz
  }));
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

    <SelectField
      id="timezone"
      label="Timezone"
      bind:value={settingsState.draftSettings.timezone}
      options={timezoneOptions}
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
    background: white;
    border: 1px solid #cfc9b9;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 24px;
    height: 100%;
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
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
</style>
