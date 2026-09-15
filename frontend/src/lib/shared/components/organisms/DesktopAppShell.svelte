<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { DesktopWindowService } from '$lib/platform/desktopWindow';
  import { desktopWindowService } from '$lib/platform/desktopWindow';
  import FixedCanvas from '../templates/FixedCanvas.svelte';
  import AppSidebar from './AppSidebar.svelte';
  import DesktopTitleBar from './DesktopTitleBar.svelte';

  let {
    activeRoute = 'TODAY',
    variant = 'standard',
    showSidebar = true,
    canvasWidth = 'var(--bloom-app-canvas-width)',
    canvasHeight = 'var(--bloom-app-canvas-height)',
    windowService = desktopWindowService,
    onTitleBarAction = () => {},
    overlay,
    children
  }: {
    activeRoute?: 'TODAY' | 'GOALS' | 'MR. BLOOM' | 'SETTINGS';
    variant?: 'standard' | 'compact';
    showSidebar?: boolean;
    canvasWidth?: string;
    canvasHeight?: string;
    windowService?: DesktopWindowService;
    onTitleBarAction?: (action: 'minimize' | 'maximize' | 'close') => void;
    overlay?: Snippet;
    children: Snippet;
  } = $props();
</script>

<FixedCanvas width={canvasWidth} height={canvasHeight} label="Blooming desktop window">
  <div class="desktop-shell desktop-shell--{variant}" class:without-sidebar={!showSidebar}>
    <DesktopTitleBar {variant} {windowService} onAction={onTitleBarAction} />
    <div class="desktop-shell__body">
      {#if showSidebar}
        <AppSidebar {activeRoute} />
      {/if}
      <div class="desktop-shell__main">
        {@render children()}
      </div>
    </div>
    {@render overlay?.()}
  </div>
</FixedCanvas>

<style>
  .desktop-shell {
    position: relative;
    display: flex;
    width: 100%;
    height: 100%;
    flex-direction: column;
    overflow: hidden;
    border: var(--bloom-frame-width) solid var(--bloom-frame);
    border-radius: 8px;
    background: var(--bloom-surface-cream);
    box-shadow:
      0 0 0 1px var(--bloom-titlebar-edge),
      inset 0 0 0 1px color-mix(in srgb, var(--bloom-titlebar-edge) 30%, white);
  }

  .desktop-shell__body {
    display: grid;
    min-height: 0;
    flex: 1;
    grid-template-columns: var(--bloom-sidebar-standard-width) minmax(0, 1fr);
  }

  .desktop-shell__main {
    height: 100%;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
  }

  .desktop-shell--compact .desktop-shell__body {
    grid-template-columns: var(--bloom-sidebar-compact-width) minmax(0, 1fr);
  }

  .desktop-shell--compact :global(.sidebar) {
    padding-top: 45px;
    background: #f4faf6;
  }

  .desktop-shell--compact :global(.sidebar-nav) {
    gap: 8px;
  }

  .desktop-shell--compact :global(.nav-item) {
    gap: 10px;
    padding-right: 5px;
    padding-left: 5px;
    font-size: 16px;
    min-height: 56px;
  }

  .desktop-shell--compact :global(.nav-item .app-icon) {
    width: 35px !important;
    height: 35px !important;
  }

  .desktop-shell--compact :global(.nav-item img.app-icon) {
    transform: scale(1.5);
  }

  .desktop-shell--compact :global(.plant-container .plant) {
    transform: translateY(8px) scale(1.67);
  }

  .desktop-shell--compact :global(.plant-container) {
    transform: translateX(1px);
  }

  .desktop-shell--compact :global(.counters) {
    transform: translateX(-5px);
  }

  .desktop-shell.without-sidebar .desktop-shell__body {
    grid-template-columns: minmax(0, 1fr);
  }
</style>
