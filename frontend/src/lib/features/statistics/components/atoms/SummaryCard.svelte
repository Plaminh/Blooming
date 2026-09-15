<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { IconName } from '$lib/shared/components/atoms/AppIcon.svelte';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { iconName, label, value }: {
    iconName: IconName;
    label: string;
    value: Snippet;
  } = $props();
</script>

<div class="summary-card">
  <div class="summary-card-header">
    <div class="icon-wrapper">
      <AppIcon name={iconName} size="task-type" />
    </div>
    <span class="label">{label}</span>
  </div>
  <div class="summary-card-value">
    {@render value()}
  </div>
</div>

<style>
  .summary-card {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 0;
    padding: 16px;
    background: var(--color-surface);
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 8px;
    gap: 12px;
  }
  
  .summary-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--bloom-text-muted-blue);
  }
  
  .label {
    font-family: var(--bloom-body-font);
    font-size: 12px;
    font-weight: 700;
    color: var(--bloom-text-muted-blue);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .summary-card-value {
    font-family: var(--bloom-body-font);
    font-size: 24px;
    font-weight: 700;
    color: var(--bloom-text-dark-blue);
  }
</style>
