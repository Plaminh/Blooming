<script lang="ts">
  import UnlockButton from '../atoms/UnlockButton.svelte';
  import UnlockCost from '../molecules/UnlockCost.svelte';
  
  let { 
    cost, 
    isUnlocked, 
    canUnlock, 
    onUnlock 
  }: { 
    cost: number; 
    isUnlocked: boolean; 
    canUnlock: boolean; 
    onUnlock: () => void; 
  } = $props();
</script>

<div class="unlock-panel">
  <UnlockButton 
    disabled={!canUnlock && !isUnlocked} 
    onclick={onUnlock} 
    text={isUnlocked ? 'SELECTED' : 'UNLOCK'}
  />
  <UnlockCost {cost} {isUnlocked} />
</div>

<style>
  .unlock-panel {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 24px;
  }
</style>
