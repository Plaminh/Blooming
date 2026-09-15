<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  let { balance }: { balance: number } = $props();
</script>

<div class="leaf-balance" aria-label="Leaf balance: {balance}">
  <AppIcon name="sprout" scale={1} />
  <span>{balance}</span>
</div>

<style>
  .leaf-balance {
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
