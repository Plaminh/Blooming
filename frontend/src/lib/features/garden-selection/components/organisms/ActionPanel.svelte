<script lang="ts">
  import UnlockButton from '../atoms/UnlockButton.svelte';
  import UnlockCost from '../molecules/UnlockCost.svelte';
  
  let { 
    cost, 
    isUnlocked,
    isSelected,
    canUnlock, 
    canWater,
    vitality,
    onUnlock,
    onSelect,
    onWater
  }: { 
    cost: number; 
    isUnlocked: boolean; 
    isSelected: boolean;
    canUnlock: boolean; 
    canWater: boolean;
    vitality: number;
    onUnlock: () => void; 
    onSelect: () => void;
    onWater: () => void;
  } = $props();
</script>

<div class="action-panel">
  {#if !isUnlocked}
    <UnlockButton 
      disabled={!canUnlock} 
      onclick={onUnlock} 
      text={'UNLOCK'}
    />
    <UnlockCost {cost} {isUnlocked} />
  {:else if !isSelected}
    <UnlockButton 
      disabled={false} 
      onclick={onSelect} 
      text={'SELECT'}
    />
  {:else}
    <UnlockButton 
      disabled={!canWater} 
      onclick={onWater} 
      text={'WATER'}
    />
    <div class="vitality">Vitality: {vitality}%</div>
  {/if}
</div>

<style>
  .action-panel {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 6px;
  }
  .vitality {
    margin-top: 4px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    color: var(--bloom-text-dark-blue);
  }
</style>
