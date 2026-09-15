<script lang="ts">
  import type { DesktopWindowService } from '$lib/platform/desktopWindow';
  import DesktopTitleBar from '$lib/shared/components/organisms/DesktopTitleBar.svelte';
  import GardenSelectionContent from './GardenSelectionContent.svelte';

  let { open, onClose }: { open: boolean; onClose: () => void } = $props();
  let dialog = $state<HTMLDialogElement>();
  let maximized = $state(false);

  function trapFocus(event: KeyboardEvent) {
    if (event.key !== 'Tab' || !dialog) return;
    const buttons = [...dialog.querySelectorAll<HTMLButtonElement>('button:not([disabled])')];
    const target = event.shiftKey ? buttons.at(-1) : buttons[0];
    const boundary = event.shiftKey ? buttons[0] : buttons.at(-1);
    if (target && document.activeElement === boundary) {
      event.preventDefault();
      target.focus();
    }
  }

  const closeWindow = async () => { dialog?.close(); };
  const windowService: DesktopWindowService = {
    openMainWindow: async () => {},
    minimizeCurrent: closeWindow,
    hideCurrent: closeWindow,
    closeCurrent: closeWindow,
    isCurrentMaximized: async () => maximized,
    toggleMaximizeCurrent: async () => { maximized = !maximized; return maximized; },
    startDraggingCurrent: async () => {},
  };

  $effect(() => {
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    else if (!open && dialog.open) dialog.close();
  });
</script>

<dialog
  bind:this={dialog}
  class="garden-selection-dialog"
  class:maximized
  aria-label="Choose your plant"
  onkeydown={trapFocus}
  onclose={onClose}
>
  <DesktopTitleBar variant="compact" {windowService} />
  <div class="garden-selection-dialog-content">
    <GardenSelectionContent />
  </div>
</dialog>

<style>
  .garden-selection-dialog {
    width: min(var(--bloom-garden-canvas-width), calc(100vw - 24px));
    height: min(var(--bloom-garden-canvas-height), calc(100vh - 24px));
    max-width: none;
    max-height: none;
    margin: auto;
    padding: 0;
    overflow: hidden;
    border: var(--bloom-frame-width) solid var(--bloom-frame);
    border-radius: 8px;
    background: var(--bloom-surface-cream);
    box-shadow: 0 12px 36px #12303a40;
  }
  .garden-selection-dialog[open] {
    display: flex;
    flex-direction: column;
  }
  .garden-selection-dialog.maximized {
    width: calc(100vw - 24px);
    height: calc(100vh - 24px);
  }
  .garden-selection-dialog::backdrop {
    background: #12303a40;
    backdrop-filter: blur(3px);
  }
  .garden-selection-dialog-content {
    flex: 1;
    min-height: 0;
    overflow: auto;
  }
</style>
