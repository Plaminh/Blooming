<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  type StatusProps = 
    | { variant?: 'tag'; status: 'Core' | 'Optional' }
    | { variant: 'pill'; status: 'Completed' | 'Unfinished' };

  let { status, variant = 'tag' }: StatusProps = $props();
</script>

{#if variant === 'tag' && (status === 'Core' || status === 'Optional')}
  <div class="status-badge tag {status.toLowerCase()}">
    {status}
  </div>
{:else if variant === 'pill' && (status === 'Completed' || status === 'Unfinished')}
  <div class="status-badge pill" class:completed={status === 'Completed'} class:unfinished={status === 'Unfinished'}>
    {#if status === 'Completed'}
      <AppIcon name="check_circle" size="task-type" />
    {:else if status === 'Unfinished'}
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="unfinished-icon">
        <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
      </svg>
    {/if}
    <span class="label">{status}</span>
  </div>
{:else}
  <!-- Unknown status/variant combination explicitly throws or returns nothing. -->
{/if}

<style>
  /* Tag Variant */
  .status-badge.tag {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: var(--bloom-body-font);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
  }
  
  .status-badge.tag.core {
    background: var(--bloom-tag-core-bg);
    color: var(--bloom-tag-core-text);
    border: 1px solid var(--bloom-tag-core-border);
  }
  
  .status-badge.tag.optional {
    background: var(--bloom-tag-optional-bg);
    color: var(--bloom-tag-optional-text);
    border: 1px solid var(--bloom-border-subtle);
  }

  /* Pill Variant */
  .status-badge.pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 16px;
    font-family: var(--bloom-body-font);
    font-size: 13px;
    font-weight: 600;
  }

  .status-badge.pill.completed {
    background: var(--bloom-task-completed-bg);
    color: var(--bloom-primary-green-border);
  }

  .status-badge.pill.unfinished {
    background: var(--bloom-surface-dark-cream);
    color: var(--bloom-text-muted-blue);
  }
  
  .unfinished-icon {
    width: var(--bloom-icon-task-type);
    height: var(--bloom-icon-task-type);
  }
</style>
