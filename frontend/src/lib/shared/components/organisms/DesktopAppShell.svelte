<script lang="ts">
  import type { Snippet } from 'svelte';
  import AppSidebar from './AppSidebar.svelte';
  import DesktopTitleBar from './DesktopTitleBar.svelte';

  let {
    activeRoute,
    children
  }: {
    activeRoute: 'TODAY' | 'GOALS' | 'MR. BLOOM' | 'SETTINGS';
    children: Snippet;
  } = $props();
</script>

<div class="desktop-shell">
  <DesktopTitleBar />
  <div class="desktop-shell__body">
    <AppSidebar {activeRoute} />
    <main class="desktop-shell__main">
      {@render children()}
    </main>
  </div>
</div>

<style>
  .desktop-shell {
    display: flex;
    width: 100vw;
    height: 100vh;
    min-width: 1000px;
    min-height: 700px;
    flex-direction: column;
    overflow: hidden;
    border: 2px solid var(--bloom-frame);
    border-radius: 8px;
    background: var(--bloom-surface-cream);
    box-shadow: 0 0 0 1px #29b9ce, inset 0 0 0 1px #d8f6f4;
  }

  .desktop-shell :global(.desktop-titlebar) {
    height: 54px;
    flex-basis: 54px;
    background: linear-gradient(180deg, #3f9ab1 0%, #3b8da5 100%);
    box-shadow: inset 0 2px 0 #61cbd5;
  }

  .desktop-shell :global(.desktop-titlebar__logo) {
    width: 50px;
    height: 50px;
    transform: translateX(-2px);
  }

  .desktop-shell :global(.desktop-titlebar__brand) {
    gap: 8px;
  }

  .desktop-shell__body {
    display: grid;
    min-height: 0;
    flex: 1;
    grid-template-columns: 181px minmax(0, 1fr);
  }

  .desktop-shell__main {
    min-width: 0;
    min-height: 0;
    overflow: hidden;
  }
</style>
