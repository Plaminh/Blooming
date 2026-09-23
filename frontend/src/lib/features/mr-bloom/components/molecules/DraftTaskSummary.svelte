<script lang="ts">
  import { mrBloomStore, type DraftTask, type Importance } from '../../stores/mrBloomStore';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { task }: { task: DraftTask } = $props();

  function handleDurationChange(event: Event) {
    const value = Number.parseInt((event.currentTarget as HTMLInputElement).value, 10);
    if (Number.isFinite(value) && value > 0) mrBloomStore.updateTaskDuration(task.id, value);
  }

  function handlePriorityChange(event: Event) {
    mrBloomStore.updateTaskImportance(task.id, (event.currentTarget as HTMLSelectElement).value as Importance);
  }

  function handleConstraintChange(updates: Partial<typeof task>) {
    let { fixedStart, fixedEnd, deadline, durationMin } = task;
    
    if ('fixedStart' in updates) fixedStart = updates.fixedStart!;
    if ('fixedEnd' in updates) fixedEnd = updates.fixedEnd!;
    if ('deadline' in updates) deadline = updates.deadline!;

    if (fixedStart && fixedEnd) {
      const [sh, sm] = fixedStart.split(':').map(Number);
      const [eh, em] = fixedEnd.split(':').map(Number);
      const duration = (eh * 60 + em) - (sh * 60 + sm);
      if (duration > 0) durationMin = duration;
    }
    
    mrBloomStore.applyPatch([{
      op: 'update_task',
      task_id: task.id,
      fixed_start: fixedStart,
      fixed_end: fixedEnd,
      deadline: deadline,
      duration_min: durationMin,
      scheduling_type: fixedStart || fixedEnd ? 'FIXED' : 'FLEXIBLE'
    }]);
  }
</script>

<article class="draft-task-row">
  <div class="main-row">
    <span class="task-icon"><AppIcon name="document" size="task-type" /></span>
    <strong class="task-title" title={task.title}>{task.title}</strong>

    <div class="duration-editor">
      <span class="sr-only">Duration for {task.title}</span>
      <span class="number-field">
        <input
          type="number"
          value={task.durationMin}
          onchange={handleDurationChange}
          min="5"
          step="5"
        />
        <span class="stepper">
          <button type="button" aria-label="Increase duration for {task.title}" onclick={() => mrBloomStore.updateTaskDuration(task.id, task.durationMin + 5)}>▲</button>
          <button type="button" aria-label="Decrease duration for {task.title}" disabled={task.durationMin <= 5} onclick={() => mrBloomStore.updateTaskDuration(task.id, task.durationMin - 5)}>▼</button>
        </span>
      </span>
      <span class="unit">min</span>
    </div>

    <label class="priority-editor">
      <span class="sr-only">Importance for {task.title}</span>
      <select value={task.importance} onchange={handlePriorityChange}>
        <option value="CORE">Must do</option>
        <option value="OPTIONAL">Optional</option>
      </select>
    </label>

    <button class="remove-btn" aria-label="Remove {task.title}" onclick={() => mrBloomStore.removeTask(task.id)}>
      <AppIcon name="close" size="control" />
    </button>
  </div>

  <div class="constraint-editor">
    {#if task.fixedStart || task.fixedEnd}
      <div class="time-range">
        <input type="time" aria-label="Start time" value={task.fixedStart ? task.fixedStart.slice(0, 5) : ''} onchange={(e) => handleConstraintChange({ fixedStart: e.currentTarget.value || null })} />
        <span>to</span>
        <input type="time" aria-label="End time" value={task.fixedEnd ? task.fixedEnd.slice(0, 5) : ''} onchange={(e) => handleConstraintChange({ fixedEnd: e.currentTarget.value || null })} />
        <button type="button" class="clear-constraint" aria-label="Clear fixed time" onclick={() => handleConstraintChange({ fixedStart: null, fixedEnd: null })}>×</button>
      </div>
    {:else if task.deadline}
      <div class="time-range">
        <span>By</span>
        <input type="time" aria-label="Deadline" value={task.deadline.slice(0, 5)} onchange={(e) => handleConstraintChange({ deadline: e.currentTarget.value || null })} />
        <button type="button" class="clear-constraint" aria-label="Clear deadline" onclick={() => handleConstraintChange({ deadline: null })}>×</button>
      </div>
    {:else}
      <details class="add-constraint">
        <summary>Add time constraint</summary>
        <div class="constraint-menu">
          <button type="button" onclick={() => handleConstraintChange({ fixedStart: '12:00' })}>Add Fixed Time</button>
          <button type="button" onclick={() => handleConstraintChange({ deadline: '17:00' })}>Add Deadline</button>
        </div>
      </details>
    {/if}
  </div>
</article>

<style>
  .draft-task-row {
    display: grid;
    min-width: 0;
    min-height: 62px;
    gap: 6px;
    padding: 7px 9px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
  }

  .draft-task-row:hover { border-color: #9fcfe4; }

  .main-row {
    display: grid;
    min-width: 0;
    grid-template-columns: var(--bloom-icon-draft-task-slot) minmax(0, 1fr) auto 104px 28px;
    align-items: center;
    gap: 8px;
  }

  .task-icon {
    display: grid;
    width: var(--bloom-icon-draft-task-slot);
    height: var(--bloom-icon-draft-task-slot);
    place-items: center;
    color: #0b657e;
  }

  .task-title {
    min-width: 0;
    overflow: hidden;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 17px;
    font-weight: 600;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .duration-editor {
    display: flex;
    flex: 0 0 auto;
    align-items: center;
    gap: 6px;
  }

  .number-field {
    position: relative;
    display: block;
    width: 72px;
    height: 38px;
  }

  .duration-editor input {
    width: 72px;
    height: 38px;
    padding: 4px 8px 4px 11px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 16px;
    outline: none;
    appearance: textfield;
  }

  .duration-editor input::-webkit-inner-spin-button,
  .duration-editor input::-webkit-outer-spin-button { appearance: none; margin: 0; }

  .stepper {
    position: absolute;
    top: 4px;
    right: 5px;
    bottom: 4px;
    display: grid;
    width: 18px;
    grid-template-rows: 1fr 1fr;
  }

  .stepper button {
    display: grid;
    min-width: 0;
    min-height: 0;
    padding: 0;
    place-items: center;
    border: 0;
    background: transparent;
    color: #064b91;
    font-size: 11px;
    line-height: 1;
    cursor: pointer;
  }

  .stepper button:disabled { opacity: 0.35; cursor: default; }

  .duration-editor input:focus-visible,
  .priority-editor select:focus-visible,
  .remove-btn:focus-visible {
    outline: 2px solid #00aeea;
    outline-offset: 2px;
  }

  .unit {
    color: #196f9f;
    font-family: var(--bloom-body-font);
    font-size: 14px;
  }

  .priority-editor { min-width: 0; }

  .priority-editor select {
    width: 100%;
    height: 38px;
    padding: 0 12px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    cursor: pointer;
  }

  .remove-btn {
    display: grid;
    width: 28px;
    height: 38px;
    padding: 0;
    place-items: center;
    border: 0;
    background: transparent;
    color: #3b7ba0;
    cursor: pointer;
  }

  .remove-btn:hover { color: #c54646; }

  .stepper button:focus-visible { outline: 1px solid #00aeea; }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  .constraint-editor {
    display: flex;
    min-width: 0;
    margin-left: calc(var(--bloom-icon-draft-task-slot) + 8px);
    flex-direction: column;
    gap: 4px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
  }
  .time-range {
    display: flex;
    min-width: 0;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
  }
  .time-range input[type="time"] {
    width: auto;
    padding: 2px 4px;
    border: 1px solid #d1cabd;
    border-radius: 4px;
    background: white;
    color: #064b91;
  }
  .clear-constraint {
    background: transparent;
    border: none;
    color: #c54646;
    cursor: pointer;
    padding: 0 4px;
  }
  .add-constraint {
    position: relative;
    width: fit-content;
  }
  .add-constraint summary {
    color: #196f9f;
    cursor: pointer;
    font-size: 12px;
    list-style: none;
  }
  .add-constraint summary::-webkit-details-marker { display: none; }
  .add-constraint summary::before { content: '+ '; }
  .constraint-menu {
    display: flex;
    gap: 4px;
    margin-top: 5px;
  }
  .constraint-menu button {
    background: #eef5f9;
    border: 1px solid #9fcfe4;
    border-radius: 4px;
    color: #0b657e;
    cursor: pointer;
    font-size: 12px;
    padding: 2px 6px;
  }

  @media (max-width: 620px) {
    .main-row { grid-template-columns: var(--bloom-icon-draft-task-slot) minmax(0, 1fr) auto 92px 28px; gap: 5px; }
    .number-field, .duration-editor input { width: 58px; }
    .priority-editor select { padding: 0 7px; font-size: 14px; }
  }
</style>
