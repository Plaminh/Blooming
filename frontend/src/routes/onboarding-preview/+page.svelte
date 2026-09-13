<script lang="ts">
  import OnboardingSetupView from '$lib/features/onboarding-setup/components/pages/OnboardingSetupView.svelte';
  import type { OnboardingSetupData } from '$lib/features/onboarding-setup/model/OnboardingSetupState.svelte';

  function handleFinish(data: OnboardingSetupData) {
    console.log('Finished with data:', data);
    alert('Finished! Check console for payload.');
  }

  function handleBack() {
    console.log('Back clicked');
    alert('Back clicked!');
  }
</script>

<svelte:head>
  <title>Blooming Onboarding</title>
</svelte:head>

<OnboardingSetupView onFinish={handleFinish} onBack={handleBack} />
