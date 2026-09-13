<script lang="ts">
  import { onMount } from 'svelte';
  import type { DesktopWindowService } from '$lib/platform/desktopWindow';
  import AuthenticationIcon from '../atoms/AuthenticationIcon.svelte';

  type TitleBarAction = 'minimize' | 'maximize' | 'close';

  let {
    windowService,
    onAction = () => {},
  }: {
    windowService: DesktopWindowService;
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
      if (target instanceof Element && target.closest('.auth-titlebar-controls')) return;
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

<header class="auth-titlebar" use:draggableTitleBar>
  <div class="auth-titlebar-brand" aria-label="Blooming">
    <img
      src="/assets/widget/icons/leaf-icon.png"
      alt=""
      class="auth-titlebar-logo"
      width="40"
      height="40"
    />
    <span class="auth-titlebar-title">BLOOMING</span>
  </div>
  <div class="auth-titlebar-controls">
    <button type="button" class="window-control" onclick={minimize} aria-label="Minimize window">
      <AuthenticationIcon name="minimize" size={19} />
    </button>
    <button
      type="button"
      class="window-control"
      onclick={toggleMaximize}
      aria-label={maximized ? 'Restore window' : 'Maximize window'}
    >
      <AuthenticationIcon name={maximized ? 'restore' : 'maximize'} size={19} />
    </button>
    <button type="button" class="window-control close" onclick={hide} aria-label="Close window">
      <AuthenticationIcon name="close" size={19} />
    </button>
  </div>
</header>
