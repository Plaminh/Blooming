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
    gap: 8px;
    background: #ffffff;
    border: 3px solid #1e3a5f;
    padding: 8px 16px;
    font-family: var(--bloom-display-font);
    font-size: 24px;
    color: #1e3a5f;
    box-shadow: 2px 2px 0px 0px rgba(0, 0, 0, 0.2);
  }
</style>
