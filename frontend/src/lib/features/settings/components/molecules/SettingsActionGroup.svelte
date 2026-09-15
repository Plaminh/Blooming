<script lang="ts">
  import { getSettingsState } from '../../model/SettingsState.svelte';

  const settingsState = getSettingsState();

  async function handleSave() {
    await settingsState.save();
  }

  function handleCancel() {
    settingsState.cancel();
  }
</script>

<div class="action-group">
  {#if settingsState.saveSuccessMessage}
    <div class="success-message" aria-live="polite">{settingsState.saveSuccessMessage}</div>
  {/if}
  
  <button 
    class="btn-cancel" 
    type="button" 
    onclick={handleCancel}
    disabled={!settingsState.isDirty || settingsState.isSaving}
  >
    CANCEL
  </button>
  
  <button 
    class="btn-save" 
    type="button" 
    onclick={handleSave}
    disabled={!settingsState.isDirty || settingsState.isSaving}
  >
    {settingsState.isSaving ? 'SAVING...' : 'SAVE CHANGES'}
  </button>
</div>

<style>
  .action-group {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 16px;
    margin-top: 16px;
  }

  .success-message {
    color: var(--bloom-primary-green);
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 600;
  }

  button {
    font-family: var(--bloom-display-font);
    font-size: 16px;
    padding: 10px 24px;
    border-radius: 4px;
    cursor: pointer;
    text-transform: uppercase;
    transition: all 0.2s ease;
  }

  button:disabled {
    opacity: 0.5;
    color: var(--bloom-disabled);
    cursor: not-allowed;
  }

  button:focus-visible {
    outline: 2px solid var(--bloom-focus);
    outline-offset: 2px;
  }

  .btn-cancel {
    background: transparent;
    border: 1px solid var(--bloom-text-dark-blue);
    color: var(--bloom-text-dark-blue);
  }

  .btn-save {
    background: var(--bloom-primary-green);
    border: 1px solid var(--bloom-primary-green);
    color: white;
  }
</style>
