<script lang="ts">
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import OnboardingSetupView from '$lib/features/onboarding-setup/components/pages/OnboardingSetupView.svelte';
  import type { OnboardingSetupData } from '$lib/features/onboarding-setup/model/OnboardingSetupState.svelte';
  import { desktop } from '$lib/platform/desktopWindow';
  import type { UserSettingsResponse } from '$lib/api/types';
  import { onMount } from 'svelte';
  import { authoritativeSettings } from '$lib/features/settings/model/userSettingsMapping';
  import { onboardingToSettingsPayload, settingsResponseToOnboarding } from '$lib/features/onboarding-setup/model/mappers';

  let initialData = $state<Partial<OnboardingSetupData> | null>(null);
  let loadError = $state('');

  onMount(async () => {
    try {
      const saved = await api.get('/me/settings') as UserSettingsResponse;
      authoritativeSettings.set(saved);
      initialData = settingsResponseToOnboarding(saved);
    } catch (error) {
      loadError = error instanceof Error ? error.message : 'Could not load your saved settings.';
    }
  });

  async function handleFinish(data: OnboardingSetupData) {
    const payload = onboardingToSettingsPayload(data);
    const saved = await api.put('/me/settings', payload) as UserSettingsResponse;
    authoritativeSettings.set(saved);
    try { await desktop.reconcileSettings(saved); } catch { /* Backend save remains authoritative. */ }
    if (typeof window !== 'undefined') window.dispatchEvent(new Event('blooming:settings-updated'));
    try {
      await desktop.settingsUpdated();
    } catch {
      // Saved settings still apply when the widget next opens or refreshes.
    }
    
    goto('/today');
  }

</script>

<svelte:head>
  <title>Blooming Onboarding</title>
</svelte:head>

{#if initialData}
  <OnboardingSetupView {initialData} onFinish={handleFinish} />
{:else if loadError}
  <div class="load-error" role="alert">{loadError} <button onclick={() => location.reload()}>Retry</button></div>
{:else}
  <div class="loading" role="status">Loading your settings…</div>
{/if}
