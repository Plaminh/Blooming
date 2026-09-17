<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  let { leaves, water }: { leaves: number, water: number } = $props();
</script>

<div class="balances">
  <div class="leaf-balance" aria-label="Leaf balance: {leaves}">
    <AppIcon name="sprout" size="garden-balance" />
    <span>{leaves}</span>
  </div>
  <div class="water-balance" aria-label="Water balance: {water}">
    <AppIcon name="water" size="garden-balance" />
    <span>{water}</span>
  </div>
</div>

<style>
  .balances {
    display: flex;
    gap: 12px;
  }
  .leaf-balance, .water-balance {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bloom-surface-cream-alt);
    border: 1px solid var(--bloom-border-dark);
    border-radius: var(--bloom-radius);
    padding: 3px 9px;
    font-family: var(--bloom-display-font);
    font-size: 24px;
    color: var(--bloom-text-dark-blue);
    box-shadow: 1px 1px 0 rgba(0, 0, 0, 0.12);
  }
</style>
