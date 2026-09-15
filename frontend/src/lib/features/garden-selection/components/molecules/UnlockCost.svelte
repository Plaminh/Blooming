<script lang="ts">
  import LockIcon from '../atoms/LockIcon.svelte';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  
  let { cost, isUnlocked }: { cost: number; isUnlocked: boolean } = $props();
</script>

{#if !isUnlocked}
  <div class="unlock-cost" aria-label="Unlock cost: {cost} leaves">
    <LockIcon class="lock" />
    <span class="cost">{cost}</span>
    <AppIcon name="sprout" size="garden-cost" />
  </div>
{:else}
  <div class="unlock-cost unlocked">
    <span>UNLOCKED</span>
  </div>
{/if}

<style>
  .unlock-cost {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-family: var(--bloom-display-font);
    font-size: 24px;
    color: var(--bloom-text-dark-blue);
    margin-top: 6px;
  }
  .unlocked span {
    color: #5db95d;
  }
</style>
