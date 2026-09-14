<script lang="ts">
  import { mrBloomStore } from '../../stores/mrBloomStore';
  import ActionButton from '../atoms/ActionButton.svelte';
  
  let { 
    primaryLabel, 
    onPrimary, 
    secondaryLabel,
    onSecondary
  }: { 
    primaryLabel: string; 
    onPrimary: () => void;
    secondaryLabel?: string;
    onSecondary?: () => void;
  } = $props();
  
  function handleDiscard() {
    mrBloomStore.discardDraft();
  }
</script>

<div class="draft-review-action-bar">
  <ActionButton label="Discard" variant="danger" onclick={handleDiscard} />
  
  <div class="right-actions">
    {#if secondaryLabel && onSecondary}
      <ActionButton label={secondaryLabel} variant="secondary" onclick={onSecondary} />
    {/if}
    <ActionButton label={primaryLabel} variant="primary" onclick={onPrimary} />
  </div>
</div>

<style>
  .draft-review-action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    background: #fdfaf3;
    border-top: 1px solid #cfc9b9;
    flex-shrink: 0;
  }
  
  .right-actions {
    display: flex;
    gap: 12px;
  }
</style>
