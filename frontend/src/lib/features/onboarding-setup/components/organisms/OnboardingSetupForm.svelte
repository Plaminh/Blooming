<script lang="ts">
  import type { OnboardingSetupState } from '../../model/OnboardingSetupState.svelte';
  import Button from '../atoms/Button.svelte';
  import Checkbox from '../atoms/Checkbox.svelte';
  import WeatherLocationPicker from '$lib/shared/components/molecules/WeatherLocationPicker.svelte';
  import FormField from '../molecules/FormField.svelte';
  import PresetSelector from '../molecules/PresetSelector.svelte';
  import TimezonePicker from '$lib/shared/components/molecules/TimezonePicker.svelte';
  import type { OnboardingErrors } from '../../model/validation';
  import { validateOnboarding } from '../../model/validation';

  let {
    state: setupState,
    pending = false,
    errors = {},
    onFinish,
  }: {
    state: OnboardingSetupState;
    pending?: boolean;
    errors?: OnboardingErrors;
    onFinish: () => void;
  } = $props();


  let selectedPresetDescription = $derived(
    setupState.focusPreset === '25 / 5'
      ? 'Work for 25 minutes, take a 5-minute break.'
      : setupState.focusPreset === '50 / 10'
        ? 'Work for 50 minutes, take a 10-minute break.'
        : 'Choose focus and break durations that suit you.',
  );

  function preventSubmit(event: SubmitEvent) {
    event.preventDefault();
  }
  let formValid = $derived(Object.keys(validateOnboarding(setupState.data)).length === 0);
</script>

<form class="setup-form-container" aria-label="Blooming setup" data-scrollable="true" onsubmit={preventSubmit}>
  <header class="form-header">
    <h2 class="form-title">Make Blooming yours</h2>
    <p class="form-subtitle">A few quick choices to get started.</p>
  </header>

  <div class="form-content">
    <div class="field-row timezone-row">
      <FormField
        id="timezone-value"
        label="Your timezone"
        description="Detected from this device for reminders and daily planning."
        descriptionId="timezone-description"
      >
        <TimezonePicker id="timezone-value" bind:value={setupState.timezone} disabled={pending}
          describedby="timezone-description timezone-error" error={errors.timezone} />
        {#if errors.timezone}<span id="timezone-error" class="field-error" role="alert">{errors.timezone}</span>{/if}
      </FormField>
    </div>

    <div class="field-row">
      <FormField
        id="weather-location"
        label="Weather location"
        description="Select a city or use approximate device location for widget weather."
        descriptionId="weather-location-description"
      >
        <WeatherLocationPicker disabled={pending} initialValue={setupState.weatherLocationName ?? ''}
          onInvalidate={() => {
            setupState.weatherLocationName = null;
            setupState.weatherLat = null;
            setupState.weatherLon = null;
          }}
          onSelect={(place: { locationName: string; lat: number; lon: number }) => {
            setupState.weatherLocationName = place.locationName;
            setupState.weatherLat = place.lat;
            setupState.weatherLon = place.lon;
          }} />
        {#if errors.weatherLocation}<span class="field-error" role="alert">{errors.weatherLocation}</span>{/if}
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
        {#if setupState.focusPreset === 'CUSTOM'}
          <div class="custom-values">
            <label for="custom-focus">Focus minutes
              <input id="custom-focus" type="number" min="1" max="720" bind:value={setupState.focusMinutes} disabled={pending} />
              {#if errors.focusMinutes}<span class="field-error" role="alert">{errors.focusMinutes}</span>{/if}
            </label>
            <label for="custom-break">Break minutes
              <input id="custom-break" type="number" min="0" max="180" bind:value={setupState.breakMinutes} disabled={pending} />
              {#if errors.breakMinutes}<span class="field-error" role="alert">{errors.breakMinutes}</span>{/if}
            </label>
          </div>
        {/if}
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
      <Button type="button" variant="primary" onclick={onFinish} disabled={pending || !formValid}>{pending ? 'SAVING…' : 'FINISH'}</Button>
    </div>
  </footer>
</form>

<style>
  .setup-form-container {
    box-sizing: border-box;
    display: flex;
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 35px 31px 15px 60px;
    overflow-x: hidden;
    overflow-y: auto;
    flex-direction: column;
    scrollbar-color: var(--bloom-border-dark) var(--bloom-surface-cream);
    scrollbar-width: thin;
    overscroll-behavior: contain;
  }

  .setup-form-container::-webkit-scrollbar { width: 10px; }
  .setup-form-container::-webkit-scrollbar-track { background: var(--bloom-surface-cream); }
  .setup-form-container::-webkit-scrollbar-thumb { border: 2px solid var(--bloom-surface-cream); border-radius: 8px; background: var(--bloom-border-dark); }

  .form-header {
    flex: 0 0 auto;
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
    width: 100%;
    margin-top: 35px;
    flex: 0 0 auto;
  }

  .timezone-row {
    margin-top: 14px;
  }

  .field-error { display: block; margin-top: 4px; color: var(--bloom-error); font-size: 14px; }
  .custom-values { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px; }
  .custom-values label { color: var(--bloom-text-dark-blue); font-size: 14px; font-weight: 600; }
  .custom-values input { box-sizing: border-box; width: 100%; height: 38px; margin-top: 4px; padding: 0 10px; border: 1px solid var(--bloom-border-subtle); border-radius: var(--bloom-radius); background: var(--bloom-surface-cream-alt); font: 17px var(--bloom-body-font); }

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
    width: 100%;
    margin-top: 26px;
    flex: 0 0 auto;
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

  .footer-actions :global(.btn-primary) {
    width: 189px;
  }
</style>
