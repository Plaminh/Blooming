<script lang="ts">
  import { onMount } from 'svelte';
  import {
    desktopWindowService,
    type DesktopWindowService,
  } from '$lib/platform/desktopWindow';

  type TitleBarAction = 'minimize' | 'maximize' | 'close';

  let {
    variant = 'standard',
    artworkVariant = variant,
    windowService = desktopWindowService,
    onAction = () => {},
  }: {
    variant?: 'standard' | 'compact';
    artworkVariant?: 'standard' | 'compact';
    windowService?: DesktopWindowService;
    onAction?: (action: TitleBarAction) => void;
  } = $props();

  let maximized = $state(false);

  onMount(() => {
    let active = true;
    void windowService.isCurrentMaximized().then((value) => {
      if (active) maximized = value;
    });
    return () => {
      active = false;
    };
  });

  function minimize() {
    onAction('minimize');
    void windowService.minimizeCurrent();
  }

  async function toggleMaximize() {
    onAction('maximize');
    maximized = await windowService.toggleMaximizeCurrent();
  }

  function hide() {
    onAction('close');
    void windowService.hideCurrent();
  }

  function draggableTitleBar(node: HTMLElement) {
    const startDragging = (event: MouseEvent) => {
      if (event.button !== 0) return;
      const target = event.target;
      if (target instanceof Element && target.closest('.desktop-titlebar__controls')) return;
      void windowService.startDraggingCurrent();
    };

    node.addEventListener('mousedown', startDragging);
    return {
      destroy() {
        node.removeEventListener('mousedown', startDragging);
      },
    };
  }
</script>

<header class="desktop-titlebar desktop-titlebar--{variant}" use:draggableTitleBar>
  <div class="desktop-titlebar__brand" aria-label="Blooming">
    <img
      src="/assets/icons/leaf-icon.png"
      alt=""
      class="desktop-titlebar__logo desktop-titlebar__logo--{artworkVariant}"
      width="40"
      height="40"
    />
    <span class="desktop-titlebar__title">BLOOMING</span>
  </div>
  <div class="desktop-titlebar__controls">
    <button class="desktop-window-control" type="button" onclick={minimize} aria-label="Minimize window">
      <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
        <path d="M3 13.5h12" stroke="currentColor" stroke-width="2.5" />
      </svg>
    </button>
    <button
      class="desktop-window-control"
      type="button"
      onclick={toggleMaximize}
      aria-label={maximized ? 'Restore window' : 'Maximize window'}
    >
      {#if maximized}
        <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
          <path d="M6 3h9v9M3 6h9v9H3z" stroke="currentColor" stroke-width="2" />
        </svg>
      {:else}
        <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
          <rect x="3" y="3" width="12" height="12" stroke="currentColor" stroke-width="2.5" />
        </svg>
      {/if}
    </button>
    <button
      class="desktop-window-control desktop-window-control--close"
      type="button"
      onclick={hide}
      aria-label="Close window"
    >
      <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
        <path d="m3.5 3.5 11 11m0-11-11 11" stroke="currentColor" stroke-width="2.5" />
      </svg>
    </button>
  </div>
</header>
