<script lang="ts">
  import UnlockButton from '../atoms/UnlockButton.svelte';
  import UnlockCost from '../molecules/UnlockCost.svelte';
  
  let { 
    cost, 
    isUnlocked,
    isSelected,
    canUnlock,
    leavesBalance,
    onUnlock,
    onSelect,
  }: { 
    cost: number; 
    isUnlocked: boolean; 
    isSelected: boolean;
    canUnlock: boolean; 
    leavesBalance: number;
    onUnlock: () => void; 
    onSelect: () => void;
  } = $props();
</script>

<div class="action-panel">
  {#if !isUnlocked}
    <UnlockButton 
      disabled={!canUnlock} 
      onclick={onUnlock} 
      text={'UNLOCK'}
    />
    <UnlockCost {cost} />
    {#if !canUnlock}
      <p class="missing-leaves" role="status">Need {cost - leavesBalance} more leaves to unlock</p>
    {/if}
  {:else if !isSelected}
    <UnlockButton 
      disabled={false} 
      onclick={onSelect} 
      text={'SELECT'}
    />
  {:else}
    <UnlockButton disabled={true} text={'SELECTED'} />
  {/if}
</div>

<style>
  .action-panel {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 6px;
  }
  .missing-leaves {
    margin: 2px 0 0;
    font-family: var(--bloom-body-font);
    font-size: 13px;
    color: var(--bloom-text-dark-blue);
  }
</style>
