<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import type { PlanStatus } from '../../types';

  let { status }: { status: PlanStatus } = $props();
</script>

<div class="status-badge" class:completed={status === 'Completed'} class:unfinished={status === 'Unfinished'}>
  {#if status === 'Completed'}
    <AppIcon name="check_circle" size="task-type" />
  {:else}
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="unfinished-icon">
      <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
    </svg>
  {/if}
  <span class="label">{status}</span>
</div>

<style>
  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 16px;
    font-family: var(--bloom-body-font);
    font-size: 13px;
    font-weight: 600;
  }

  .status-badge.completed {
    background: var(--bloom-task-completed-bg);
    color: var(--bloom-primary-green-border);
  }

  .status-badge.unfinished {
    background: var(--bloom-surface-dark-cream);
    color: var(--bloom-text-muted-blue);
  }
  
  .unfinished-icon {
    width: var(--bloom-icon-task-type);
    height: var(--bloom-icon-task-type);
  }
</style>
