<script lang="ts">
  import type { TimelineEntry } from '../../stores/mrBloomStore';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { entry }: { entry: TimelineEntry } = $props();
  
  let isBreak = $derived(entry.type === 'break');
  let isBuffer = $derived(entry.type === 'buffer');
</script>

<div class="timeline-task-summary {entry.type}">
  <div class="icon-container">
    {#if isBreak}
      <AppIcon name="local_cafe" />
    {:else if isBuffer}
      <AppIcon name="directions_walk" />
    {:else}
      <AppIcon name={entry.icon || 'check_circle'} />
    {/if}
  </div>
  
  <div class="task-info">
    <div class="task-title">{entry.title}</div>
    <div class="task-duration">{entry.durationLabel}</div>
  </div>
</div>

<style>
  .timeline-task-summary {
    display: flex;
    align-items: center;
    padding: 12px;
    background: #ffffff;
    border: 1px solid #cfc9b9;
    border-radius: 6px;
    gap: 12px;
    width: 100%;
    box-sizing: border-box;
  }
  
  .timeline-task-summary.break {
    background: #fdfaf3;
    border-style: dashed;
  }
  
  .timeline-task-summary.buffer {
    background: #fdfaf3;
    border-style: dotted;
  }
  
  .icon-container {
    color: #92b9d4;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .task-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .task-title {
    font-family: var(--bloom-body-font);
    font-size: 15px;
    color: #064798;
    font-weight: 700;
  }
  
  .task-duration {
    font-family: var(--bloom-body-font);
    font-size: 12px;
    color: #92b9d4;
  }
</style>
