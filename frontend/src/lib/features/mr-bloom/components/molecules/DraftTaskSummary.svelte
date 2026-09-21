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
</script>

<article class="draft-task-row">
  <span class="task-icon"><AppIcon name="document" size="task-type" /></span>
  <strong class="task-title">{task.title}</strong>

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
    <span class="sr-only">Priority for {task.title}</span>
    <select value={task.importance} onchange={handlePriorityChange}>
      <option value="CORE">Core</option>
      <option value="OPTIONAL">Optional</option>
    </select>
  </label>

  <button class="remove-btn" aria-label="Remove {task.title}" onclick={() => mrBloomStore.removeTask(task.id)}>
    <AppIcon name="close" size="control" />
  </button>
</article>

<style>
  .draft-task-row {
    display: flex;
    min-width: 0;
    min-height: 62px;
    align-items: center;
    gap: 8px;
    padding: 7px 9px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
  }

  .draft-task-row:hover { border-color: #9fcfe4; }

  .task-icon {
    display: grid;
    width: var(--bloom-icon-draft-task-slot);
    height: var(--bloom-icon-draft-task-slot);
    flex: 0 0 var(--bloom-icon-draft-task-slot);
    place-items: center;
    color: #0b657e;
  }

  .task-title {
    min-width: 120px;
    flex: 1;
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

  .priority-editor { flex: 0 0 104px; }

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
    flex: 0 0 28px;
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
</style>
