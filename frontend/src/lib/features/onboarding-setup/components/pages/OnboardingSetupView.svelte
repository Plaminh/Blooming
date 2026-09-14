<script lang="ts">
  import { untrack } from 'svelte';
  import type { DesktopWindowService } from '$lib/platform/desktopWindow';
  import { desktopWindowService } from '$lib/platform/desktopWindow';
  import { OnboardingSetupState, type OnboardingSetupData } from '../../model/OnboardingSetupState.svelte';
  import DesktopTitleBar from '$lib/shared/components/organisms/DesktopTitleBar.svelte';
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

<div class="onboarding-canvas">
  <div class="onboarding-stage">
    <div class="onboarding-setup-view">
      <DesktopTitleBar {windowService} />
      <main class="content-split">
        <OnboardingBrandPanel />
        <div class="form-col">
          <OnboardingSetupForm {state} onFinish={handleFinish} onBack={handleBack} />
        </div>
      </main>
    </div>
  </div>
</div>

<style>
  .onboarding-canvas {
    position: fixed;
    inset: 0;
    display: grid;
    place-items: center;
    overflow: hidden;
    background: var(--bloom-canvas);
  }

  .onboarding-stage {
    --onboarding-scale: min(
      1,
      calc((100vw - 46px) / 1394px),
      calc((100vh - 58px) / 843px)
    );

    position: relative;
    width: calc(1394px * var(--onboarding-scale));
    height: calc(843px * var(--onboarding-scale));
  }

  .onboarding-setup-view {
    position: absolute;
    top: 0;
    left: 0;
    display: flex;
    width: 1394px;
    height: 843px;
    flex-direction: column;
    overflow: hidden;
    background: var(--bloom-surface-cream);
    color: var(--bloom-text-control-blue);
    font-family: var(--bloom-body-font);
    transform: scale(var(--onboarding-scale));
    transform-origin: top left;
  }

  .onboarding-setup-view::after {
    position: absolute;
    z-index: 20;
    inset: 0;
    border: 2px solid var(--bloom-frame);
    border-radius: 8px 8px 5px 5px;
    box-shadow:
      inset 1px 1px 0 rgba(101, 189, 196, 0.7),
      inset -1px -1px 0 rgba(8, 61, 102, 0.32);
    content: '';
    pointer-events: none;
  }

  .content-split {
    display: grid;
    width: 100%;
    min-height: 0;
    flex: 1;
    grid-template-columns: 432px 1fr;
  }

  .form-col {
    display: flex;
    min-width: 0;
    flex-direction: column;
    overflow: hidden;
    background: var(--bloom-surface-cream);
  }
</style>
