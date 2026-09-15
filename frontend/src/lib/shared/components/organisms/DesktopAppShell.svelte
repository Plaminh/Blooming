<script lang="ts">
  import type { Snippet } from 'svelte';
  import AppSidebar from './AppSidebar.svelte';
  import DesktopTitleBar from './DesktopTitleBar.svelte';

  let {
    activeRoute,
    compact = false,
    children
  }: {
    activeRoute: 'TODAY' | 'GOALS' | 'MR. BLOOM' | 'SETTINGS';
    compact?: boolean;
    children: Snippet;
  } = $props();
</script>

<div class="desktop-shell" class:compact>
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

  .desktop-shell.compact :global(.desktop-titlebar) {
    height: 44px;
    flex-basis: 44px;
  }

  .desktop-shell.compact :global(.desktop-titlebar__logo) {
    width: 40px;
    height: 40px;
  }

  .desktop-shell.compact :global(.desktop-titlebar__title) {
    font-size: 21px;
  }

  .desktop-shell.compact :global(.desktop-window-control) {
    width: 29px;
    height: 28px;
  }

  .desktop-shell.compact :global(.desktop-titlebar__controls) {
    gap: 7px;
    padding-right: 9px;
  }

  .desktop-shell.compact .desktop-shell__body {
    grid-template-columns: 166px minmax(0, 1fr);
  }

  .desktop-shell.compact :global(.sidebar) {
    padding-top: 45px;
    background: #f4faf6;
  }

  .desktop-shell.compact :global(.sidebar-nav) {
    gap: 8px;
  }

  .desktop-shell.compact :global(.nav-item) {
    gap: 15px;
    font-size: 18px;
    min-height: 56px;
  }

  .desktop-shell.compact :global(.nav-item .app-icon) {
    width: 35px !important;
    height: 35px !important;
  }

  .desktop-shell.compact :global(.nav-item img.app-icon) {
    transform: scale(1.5);
  }

  .desktop-shell.compact :global(.plant-container .plant) {
    transform: translateY(8px) scale(1.67);
  }

  .desktop-shell.compact :global(.plant-container) {
    transform: translateX(1px);
  }

  .desktop-shell.compact :global(.counters) {
    transform: translateX(-5px);
  }
</style>
