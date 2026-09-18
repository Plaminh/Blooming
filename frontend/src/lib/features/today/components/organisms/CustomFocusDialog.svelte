<script lang="ts">
  import { api } from '$lib/api';
  import type { UserSettingsResponse } from '$lib/api/types';
  import FocusTimerFields from '$lib/features/settings/components/molecules/FocusTimerFields.svelte';
  import DesktopTitleBar from '$lib/shared/components/organisms/DesktopTitleBar.svelte';

  let { open, onClose, onSave }: {
    open: boolean;
    onClose: () => void;
    onSave: (focusMinutes: number, breakMinutes: number) => void;
  } = $props();

  let dialog = $state<HTMLDialogElement>();
  let focusMinutes = $state(25);
  let breakMinutes = $state(5);
  let loading = $state(false);
  let loaded = $state(false);
  let saving = $state(false);
  let error = $state<string | null>(null);
  let requestId = 0;

  function handleClose() {
    ++requestId;
    onClose();
  }

  async function loadSettings() {
    const id = ++requestId;
    loading = true;
    loaded = false;
    error = null;
    try {
      const settings: UserSettingsResponse = await api.get('/me/settings');
      if (id !== requestId) return;
      focusMinutes = settings.default_focus_minutes;
      breakMinutes = settings.default_break_minutes;
      loaded = true;
    } catch (cause) {
      if (id === requestId) error = cause instanceof Error ? cause.message : 'Failed to load focus settings.';
    } finally {
      if (id === requestId) loading = false;
    }
  }

  async function save() {
    if (!loaded || loading || saving) return;
    saving = true;
    error = null;
    try {
      const settings: UserSettingsResponse = await api.put('/me/settings', {
        default_focus_minutes: Number(focusMinutes),
        default_break_minutes: Number(breakMinutes),
      });
      onSave(settings.default_focus_minutes, settings.default_break_minutes);
      dialog?.close();
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Failed to save focus settings.';
    } finally {
      saving = false;
    }
  }

  $effect(() => {
    if (!dialog) return;
    if (open && !dialog.open) {
      dialog.showModal();
      void loadSettings();
    } else if (!open && dialog.open) {
      ++requestId;
      dialog.close();
    }
  });
</script>

<dialog bind:this={dialog} class="custom-focus-dialog" aria-labelledby="custom-focus-title" onclose={handleClose}>
  <DesktopTitleBar
    variant="compact"
    title="CUSTOM FOCUS TIMER"
    titleId="custom-focus-title"
    showLogo={false}
    closeLabel="Close custom focus"
    showSizeControls={false}
    draggable={false}
    onClose={() => dialog?.close()}
  />
  <div class="content">
    <p>Choose your focus and break durations.</p>
    <fieldset disabled={loading || saving}>
      <FocusTimerFields idPrefix="custom" bind:focusMinutes bind:breakMinutes />
    </fieldset>
    {#if error}<p class="error" role="alert">{error}</p>{/if}
    <div class="actions">
      <button type="button" onclick={() => dialog?.close()} disabled={saving}>Cancel</button>
      <button type="button" class="save-button" onclick={save} disabled={!loaded || loading || saving}>{saving ? 'Saving...' : 'Save'}</button>
    </div>
  </div>
</dialog>

<style>
  .custom-focus-dialog {
    width: min(540px, calc(100vw - 24px));
    max-width: none;
    max-height: calc(100vh - 24px);
    margin: auto;
    padding: 0;
    border: 2px solid var(--bloom-frame);
    border-radius: 6px;
    background: var(--bloom-surface-cream);
    color: var(--bloom-text-dark-blue);
    box-shadow: 0 12px 36px #12303a40;
  }
  .custom-focus-dialog::backdrop {
    background: #12303a80;
    backdrop-filter: blur(3px);
  }
  .custom-focus-dialog :global(.desktop-titlebar__brand) { padding-left: 12px; }
  .content { padding: 20px 18px 16px; font-family: var(--bloom-body-font); }
  .content > p:first-child { margin: 0 0 20px; }
  fieldset { min-width: 0; margin: 0; padding: 0; border: 0; }
  .error { color: var(--bloom-error); }
  .actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 12px; }
  .actions button {
    min-width: 100px;
    padding: 9px 16px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 4px;
    background: var(--bloom-surface-cream-alt);
    color: var(--bloom-text-dark-blue);
    font: inherit;
    font-weight: 700;
    cursor: pointer;
  }
  .actions .save-button { background: var(--bloom-action-primary-bg); color: white; }
  button:focus-visible { outline: 2px solid var(--bloom-focus); outline-offset: 2px; }
</style>
