<script lang="ts">
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import OnboardingSetupView from '$lib/features/onboarding-setup/components/pages/OnboardingSetupView.svelte';
  import type { OnboardingSetupData } from '$lib/features/onboarding-setup/model/OnboardingSetupState.svelte';
  import { desktop } from '$lib/platform/desktopWindow';

  async function handleFinish(data: OnboardingSetupData) {
    const defaultFocusMinutes = data.focusPreset === '50 / 10' ? 50 : 25;
    const defaultBreakMinutes = data.focusPreset === '50 / 10' ? 10 : 5;
    
    await api.put('/me/settings', {
      mr_bloom_display_name: data.name,
      timezone: data.timezone,
      default_focus_minutes: defaultFocusMinutes,
      default_break_minutes: defaultBreakMinutes,
      launch_on_startup: data.startAtLogin,
      widget_always_on_top: data.keepWidgetOnTop,
      weather_location_name: data.weatherLocationName,
      weather_lat: data.weatherLat,
      weather_lon: data.weatherLon,
      weather_enabled: data.weatherLat !== null && data.weatherLon !== null,
    });
    if (typeof window !== 'undefined') window.dispatchEvent(new Event('blooming:settings-updated'));
    try {
      await desktop.settingsUpdated();
    } catch {
      // Saved settings still apply when the widget next opens or refreshes.
    }
    
    goto('/today');
  }

  function handleBack() {
    goto('/');
  }
</script>

<svelte:head>
  <title>Blooming Onboarding</title>
</svelte:head>

<OnboardingSetupView onFinish={handleFinish} onBack={handleBack} />
