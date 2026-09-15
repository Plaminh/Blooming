<script lang="ts">
  import { untrack } from 'svelte';
  import type { DesktopWindowService } from '$lib/platform/desktopWindow';
  import { desktopWindowService } from '$lib/platform/desktopWindow';
  import { OnboardingSetupState, type OnboardingSetupData } from '../../model/OnboardingSetupState.svelte';
  import DesktopAppShell from '$lib/shared/components/organisms/DesktopAppShell.svelte';
  import OnboardingBrandPanel from '../organisms/OnboardingBrandPanel.svelte';
  import OnboardingSetupForm from '../organisms/OnboardingSetupForm.svelte';

  let {
    initialData,
    onFinish,
    onBack,
    windowService = desktopWindowService,
  }: {
    initialData?: Partial<OnboardingSetupData>;
    onFinish?: (data: OnboardingSetupData) => void;
    onBack?: () => void;
    windowService?: DesktopWindowService;
  } = $props();

  const state = new OnboardingSetupState(untrack(() => initialData));

  function handleFinish() {
    onFinish?.(state.data);
  }

  function handleBack() {
    onBack?.();
  }
</script>

<DesktopAppShell variant="compact" showSidebar={false} {windowService}>
  <main class="content-split">
    <OnboardingBrandPanel />
    <div class="form-col">
      <OnboardingSetupForm {state} onFinish={handleFinish} onBack={handleBack} />
    </div>
  </main>
</DesktopAppShell>

<style>
  .content-split {
    display: grid;
    width: 100%;
    height: 100%;
    min-height: 0;
    grid-template-columns: 398px minmax(0, 1fr);
  }

  .form-col {
    display: flex;
    min-width: 0;
    flex-direction: column;
    overflow: hidden;
    background: var(--bloom-surface-cream);
  }
</style>
