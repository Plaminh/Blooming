<script lang="ts">
  import { page } from '$app/stores';
  import DesktopAppShell from '$lib/shared/components/organisms/DesktopAppShell.svelte';
  import GardenPanel from '$lib/shared/components/organisms/GardenPanel.svelte';
  import { overlayStore } from '$lib/shared/stores/overlayStore';
  import { authStore } from '$lib/shared/stores/authStore';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  onMount(async () => {
    await authStore.initialize();
    if (!$authStore.isAuthenticated) {
      goto('/auth');
    }
  });
  
  let { children } = $props();

  let activeRoute = $derived(((): 'TODAY' | 'GOALS' | 'MR. BLOOM' | 'SETTINGS' | 'STATISTICS' => {
    const path = $page.url.pathname;
    if (path.startsWith('/today')) return 'TODAY';
    if (path.startsWith('/goals')) return 'GOALS';
    if (path.startsWith('/mr-bloom')) return 'MR. BLOOM';
    if (path.startsWith('/settings')) return 'SETTINGS';
    if (path.startsWith('/statistics')) return 'STATISTICS';
    return 'TODAY';
  })());

  let variant = $derived('compact' as const);
  
  let isGardenSelection = $derived($page.url.pathname.startsWith('/garden-selection'));
  let showSidebar = $derived(!isGardenSelection);
  let showGarden = $derived(
    $page.url.pathname.startsWith('/today') ||
    $page.url.pathname.startsWith('/goals')
  );
  let canvasWidth = $derived(isGardenSelection ? 'var(--bloom-garden-canvas-width)' : 'var(--bloom-app-canvas-width)');
  let canvasHeight = $derived(isGardenSelection ? 'var(--bloom-garden-canvas-height)' : 'var(--bloom-app-canvas-height)');
</script>

{#if $authStore.isInitialized && $authStore.isAuthenticated}
  <DesktopAppShell {activeRoute} {variant} {showSidebar} {canvasWidth} {canvasHeight} overlay={$overlayStore}
    showTitleBarSizeControls={!isGardenSelection}
    onTitleBarClose={isGardenSelection ? () => { void goto('/today'); } : undefined}>
    <div class="page-layer" style="grid-area: layer;">
      {@render children()}
    </div>
    
    {#if showGarden}
      <div class="garden-layer" class:is-goals={activeRoute === 'GOALS'} style="grid-area: layer;">
        <GardenPanel />
      </div>
    {/if}
  </DesktopAppShell>
{:else}
  <div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: var(--bloom-surface-cream);">
    <p>Loading...</p>
  </div>
{/if}

<style>
  .page-layer {
    height: 100%;
    min-width: 0;
    min-height: 0;
  }
  
  .garden-layer {
    pointer-events: none;
    display: grid;
    height: 100%;
    width: 100%;
  }
  
  .garden-layer :global(a.garden) {
    pointer-events: auto;
    height: 100%;
  }
  
  /* Today structural grid (matches .today-content) */
  .garden-layer:not(.is-goals) {
    grid-template-columns: minmax(0, 1fr) 390px;
    grid-template-rows: 210px 82px 190px minmax(0, 1fr);
    row-gap: 8px;
    column-gap: 9px;
    padding: 9px 9px 10px 0;
  }
  .garden-layer:not(.is-goals) :global(a.garden) {
    grid-column: 2;
    grid-row: 4;
  }
  
  /* Goals structural grid (matches .goals-content) */
  .garden-layer.is-goals {
    grid-template-columns: 270px 470px minmax(0, 1fr);
    grid-template-rows: minmax(0, 1fr) 278px;
    column-gap: 10px;
    padding: 10px 10px 10px 12px;
  }
  .garden-layer.is-goals :global(a.garden) {
    grid-column: 3;
    grid-row: 2;
    height: 270px;
    margin-bottom: 8px;
    grid-template-rows: 39px 1fr 58px;
  }
  .garden-layer.is-goals :global(.garden .panel-strip) { height: 39px; }
  .garden-layer.is-goals :global(.garden .garden-footer) { font-size: 16px; }
  .garden-layer.is-goals :global(.garden .garden-footer span:last-child) { font-size: 18px; }
</style>
