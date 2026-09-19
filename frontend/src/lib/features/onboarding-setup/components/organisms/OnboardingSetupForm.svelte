<script lang="ts">
  import type { OnboardingSetupState } from '../../model/OnboardingSetupState.svelte';
  import Button from '../atoms/Button.svelte';
  import Checkbox from '../atoms/Checkbox.svelte';
  import Input from '../atoms/Input.svelte';
  import { requestDeviceLocation, isDeviceCoordinates } from '$lib/shared/deviceLocation';
  import FormField from '../molecules/FormField.svelte';
  import PresetSelector from '../molecules/PresetSelector.svelte';
  import StepProgress from '../molecules/StepProgress.svelte';

  let {
    state: setupState,
    pending = false,
    onFinish,
    onBack,
  }: {
    state: OnboardingSetupState;
    pending?: boolean;
    onFinish: () => void;
    onBack: () => void;
  } = $props();

  let locationPending = $state(false);
  let locationError = $state<string | null>(null);

  async function useDeviceLocation() {
    locationPending = true;
    locationError = null;
    try {
      setupState.weatherLocation = await requestDeviceLocation();
    } catch (error) {
      locationError = error instanceof Error ? error.message : 'Could not get device location.';
    } finally {
      locationPending = false;
    }
  }

  let selectedPresetDescription = $derived(
    setupState.focusPreset === '25 / 5'
      ? 'Work for 25 minutes, take a 5-minute break.'
      : setupState.focusPreset === '50 / 10'
        ? 'Work for 50 minutes, take a 10-minute break.'
        : 'Configure your own focus and break durations later.',
  );

  function submit(event: SubmitEvent) {
    event.preventDefault();
    onFinish();
  }
</script>

<form class="setup-form-container" aria-label="Blooming setup" onsubmit={submit}>
  <div class="stepper-slot">
    <StepProgress currentStep={1} />
  </div>

  <header class="form-header">
    <h2 class="form-title">Make Blooming yours</h2>
    <p class="form-subtitle">A few quick choices to get started.</p>
  </header>

  <div class="form-content">
    <div class="field-row name-row">
      <FormField
        id="name-input"
        label="Mr. Bloom's name"
        description="This is what we'll call your friend."
        descriptionId="name-description"
      >
        <Input
          id="name-input"
          bind:value={setupState.name}
          ariaDescribedby="name-description"
          disabled={pending}
        />
      </FormField>
    </div>

    <div class="field-row timezone-row">
      <FormField
        id="timezone-value"
        label="Your timezone"
        description="Detected from this device for reminders and daily planning."
        descriptionId="timezone-description"
      >
        <output id="timezone-value" class="device-timezone" aria-describedby="timezone-description">{setupState.timezone}</output>
      </FormField>
    </div>

    <div class="field-row">
      <FormField
        id="weather-location"
        label="Weather location (optional)"
        description="Use device location, or enter a city for widget weather."
        descriptionId="weather-location-description"
      >
        <Input
          id="weather-location"
          bind:value={setupState.weatherLocation}
          placeholder="City, country"
          maxlength={100}
          ariaDescribedby="weather-location-description"
          disabled={pending}
        />
        <button type="button" class="location-button" disabled={pending || locationPending} onclick={useDeviceLocation}>
          {locationPending ? 'Finding location...' : 'Use device location'}
        </button>
        {#if isDeviceCoordinates(setupState.weatherLocation)}<span role="status">Device location selected</span>{/if}
        {#if locationError}<span role="alert">{locationError}</span>{/if}
      </FormField>
    </div>

    <div class="field-row preset-row">
      <FormField
        label="Focus session preset"
        labelId="preset-label"
        description={selectedPresetDescription}
        descriptionId="preset-description"
      >
        <PresetSelector
          bind:selected={setupState.focusPreset}
          labelledby="preset-label"
          describedby="preset-description"
          disabled={pending}
        />
      </FormField>
    </div>

    <div class="field-row options-row">
      <FormField label="Additional options" labelId="options-label">
        <div class="options-list" role="group" aria-labelledby="options-label">
          <Checkbox
            id="start-at-login"
            bind:checked={setupState.startAtLogin}
            label="Start Blooming at login"
            description="Let Blooming greet you when you start your computer."
            disabled={pending}
          />
          <Checkbox
            id="keep-widget-on-top"
            bind:checked={setupState.keepWidgetOnTop}
            label="Keep widget on top"
            description="Keep the Blooming widget above other windows."
            disabled={pending}
          />
        </div>
      </FormField>
    </div>
  </div>

  <footer class="form-footer">
    <div class="footer-divider"></div>
    <div class="footer-actions">
      <Button type="button" variant="secondary" onclick={onBack} disabled={pending}>BACK</Button>
      <Button type="submit" variant="primary" disabled={pending}>FINISH</Button>
    </div>
  </footer>
</form>

<style>
  .setup-form-container {
    position: relative;
    width: 100%;
    height: 100%;
    margin: 0;
    overflow: hidden;
  }

  .stepper-slot {
    position: absolute;
    top: 30px;
    left: 44px;
    width: 790px;
  }

  .form-header {
    position: absolute;
    top: 145px;
    left: 60px;
  }

  .form-title {
    margin: 0;
    color: var(--bloom-text-dark-blue);
    font-family: var(--bloom-display-font);
    font-size: 43px;
    font-weight: 900;
    letter-spacing: 0.015em;
    line-height: 1.16;
  }

  .form-subtitle {
    margin: 5px 0 0;
    color: var(--bloom-text-muted-blue);
    font-family: var(--bloom-body-font);
    font-size: 20px;
    line-height: 1.4;
  }

  .form-content {
    position: absolute;
    top: 250px;
    bottom: 95px;
    left: 60px;
    width: 755px;
    overflow-y: auto;
    padding-right: 8px;
  }

  .timezone-row {
    margin-top: 14px;
  }

  .device-timezone {
    display: flex;
    min-height: 42px;
    align-items: center;
    padding: 0 14px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: var(--bloom-radius);
    background: var(--bloom-surface-cream-alt);
    color: var(--bloom-text-control-blue);
    font: 19px var(--bloom-body-font);
  }

  .location-button {
    align-self: flex-start;
    margin-top: 8px;
    padding: 7px 12px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: var(--bloom-radius);
    background: var(--bloom-surface-cream-alt);
    color: var(--bloom-text-dark-blue);
    cursor: pointer;
  }

  .preset-row {
    margin-top: 22px;
  }

  .options-row {
    margin-top: 23px;
  }

  .options-list {
    display: flex;
    flex-direction: column;
    gap: 17px;
  }

  .form-footer {
    position: absolute;
    right: 31px;
    bottom: 15px;
    left: 28px;
  }

  .footer-divider {
    height: 1px;
    margin-bottom: 15px;
    background: var(--bloom-border-subtle);
  }

  .footer-actions {
    display: flex;
    justify-content: flex-end;
    gap: 14px;
  }

  .footer-actions :global(.btn-secondary) {
    width: 167px;
  }

  .footer-actions :global(.btn-primary) {
    width: 189px;
  }
</style>
