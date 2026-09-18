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
    artworkVariant = variant,
    showSidebar = true,
    canvasWidth = 'var(--bloom-app-canvas-width)',
    canvasHeight = 'var(--bloom-app-canvas-height)',
    windowService = desktopWindowService,
    onTitleBarAction = () => {},
    showTitleBarSizeControls = true,
    onTitleBarClose,
    overlay,
    children
  }: {
    activeRoute?: 'TODAY' | 'GOALS' | 'MR. BLOOM' | 'SETTINGS' | 'STATISTICS';
    variant?: 'standard' | 'compact';
    artworkVariant?: 'standard' | 'compact';
    showSidebar?: boolean;
    canvasWidth?: string;
    canvasHeight?: string;
    windowService?: DesktopWindowService;
    onTitleBarAction?: (action: 'minimize' | 'maximize' | 'close') => void;
    showTitleBarSizeControls?: boolean;
    onTitleBarClose?: () => void;
    overlay?: Snippet;
    children: Snippet;
  } = $props();
</script>

<FixedCanvas width={canvasWidth} height={canvasHeight} label="Blooming desktop window">
  <div class="desktop-shell desktop-shell--{variant}" class:without-sidebar={!showSidebar}>
    <DesktopTitleBar {variant} {artworkVariant} {windowService} onAction={onTitleBarAction} showSizeControls={showTitleBarSizeControls} onClose={onTitleBarClose} />
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
    position: relative;
    height: 100%;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
    display: grid;
    grid-template-areas: "layer";
  }

  .desktop-shell--compact .desktop-shell__body {
    grid-template-columns: var(--bloom-sidebar-compact-width) minmax(0, 1fr);
  }

  .desktop-shell.without-sidebar .desktop-shell__body {
    grid-template-columns: minmax(0, 1fr);
  }
</style>
