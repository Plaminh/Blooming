<script lang="ts">
  import { untrack } from 'svelte';
  import type { DesktopWindowService } from '$lib/platform/desktopWindow';
  import { desktopWindowService } from '$lib/platform/desktopWindow';
  import { OnboardingSetupState, type OnboardingSetupData } from '../../model/OnboardingSetupState.svelte';
  import DesktopAppShell from '$lib/shared/components/organisms/DesktopAppShell.svelte';
  import OnboardingBrandPanel from '../organisms/OnboardingBrandPanel.svelte';
  import OnboardingSetupForm from '../organisms/OnboardingSetupForm.svelte';
  import { validateOnboarding, type OnboardingErrors } from '../../model/validation';

  let {
    initialData,
    onFinish,
    windowService = desktopWindowService,
  }: {
    initialData?: Partial<OnboardingSetupData>;
    onFinish?: (data: OnboardingSetupData) => void | Promise<void>;
    windowService?: DesktopWindowService;
  } = $props();

  let pending = $state(false);
  let errorMessage = $state<string | null>(null);
  let validationErrors = $state<OnboardingErrors>({});
  const setupState = new OnboardingSetupState(untrack(() => initialData));

  async function handleFinish() {
    if (pending) return;
    validationErrors = validateOnboarding(setupState.data);
    if (Object.keys(validationErrors).length) return;
    pending = true;
    errorMessage = null;
    try {
      if (onFinish) {
        await onFinish(setupState.data);
      }
    } catch (e: any) {
      errorMessage = e?.message || 'Failed to complete setup. Please try again.';
    } finally {
      pending = false;
    }
  }

</script>

<DesktopAppShell variant="compact" showSidebar={false} {windowService}>
  <main class="content-split">
    <OnboardingBrandPanel />
    <div class="form-col">
      {#if errorMessage}
        <div class="error-banner" role="alert" aria-live="assertive">
          {errorMessage}
        </div>
      {/if}
      <OnboardingSetupForm state={setupState} {pending} errors={validationErrors} onFinish={handleFinish} />
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
    position: relative;
  }

  .error-banner {
    position: absolute;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--bloom-error);
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 600;
    z-index: 10;
    white-space: nowrap;
  }
</style>
