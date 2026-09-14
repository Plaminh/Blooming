<script lang="ts">
  import { mrBloomStore, type DraftTask } from '../../stores/mrBloomStore';
  import StatusBadge from '../atoms/StatusBadge.svelte';
  import IconButton from '../atoms/IconButton.svelte';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { task }: { task: DraftTask } = $props();
  
  function handleDurationChange(e: Event) {
    const target = e.target as HTMLInputElement;
    const val = parseInt(target.value);
    if (!isNaN(val) && val > 0) {
      mrBloomStore.updateTaskDuration(task.id, val);
    }
  }
</script>

<div class="draft-task-summary">
  <div class="drag-handle">
    <AppIcon name="drag-indicator" />
  </div>
  
  <div class="task-info">
    <div class="task-title">{task.title}</div>
    <div class="task-meta">
      <StatusBadge status={task.priority} />
    </div>
  </div>
  
  <div class="task-controls">
    <div class="duration-control">
      <input 
        type="number" 
        value={task.durationMin} 
        onchange={handleDurationChange}
        min="5" 
        step="5"
        aria-label="Duration in minutes"
      />
      <span class="unit">min</span>
    </div>
    
    <IconButton icon="close" label="Remove task" variant="ghost" size="small" />
  </div>
</div>

<style>
  .draft-task-summary {
    display: flex;
    align-items: center;
    padding: 12px;
    background: #ffffff;
    border: 1px solid #cfc9b9;
    border-radius: 6px;
    gap: 12px;
    margin-bottom: 8px;
    transition: all 0.2s;
  }
  
  .draft-task-summary:hover {
    border-color: #a9e0f5;
  }
  
  .drag-handle {
    color: #cfc9b9;
    cursor: grab;
    display: flex;
    align-items: center;
  }
  
  .task-info {
    flex: 1;
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
  
  .task-controls {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .duration-control {
    display: flex;
    align-items: center;
    gap: 4px;
    background: #fdfaf3;
    border: 1px solid #cfc9b9;
    border-radius: 4px;
    padding: 2px 8px;
  }
  
  .duration-control input {
    width: 40px;
    border: none;
    background: transparent;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    color: #064798;
    text-align: right;
    outline: none;
  }
  
  .duration-control input::-webkit-inner-spin-button {
    opacity: 1;
  }
  
  .unit {
    font-family: var(--bloom-body-font);
    font-size: 12px;
    color: #92b9d4;
  }
</style>
