<script lang="ts">
  import { mrBloomStore, type DraftTask, type Priority } from '../../stores/mrBloomStore';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { task }: { task: DraftTask } = $props();

  function handleDurationChange(event: Event) {
    const value = Number.parseInt((event.currentTarget as HTMLInputElement).value, 10);
    if (Number.isFinite(value) && value > 0) mrBloomStore.updateTaskDuration(task.id, value);
  }

  function handlePriorityChange(event: Event) {
    mrBloomStore.updateTaskPriority(task.id, (event.currentTarget as HTMLSelectElement).value as Priority);
  }
</script>

<article class="draft-task-row">
  <span class="task-icon"><AppIcon name={task.icon ?? 'document'} scale={1.9} /></span>
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
    <select value={task.priority} onchange={handlePriorityChange}>
      <option value="Core">Core</option>
      <option value="Optional">Optional</option>
    </select>
  </label>

  <button class="remove-btn" aria-label="Remove {task.title}" onclick={() => mrBloomStore.removeTask(task.id)}>
    <AppIcon name="close" scale={1.05} />
  </button>
</article>

<style>
  .draft-task-row {
    display: flex;
    min-width: 0;
    min-height: 78px;
    align-items: center;
    gap: 12px;
    padding: 10px 13px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
  }

  .draft-task-row:hover { border-color: #9fcfe4; }

  .task-icon {
    display: grid;
    width: 49px;
    height: 49px;
    flex: 0 0 49px;
    place-items: center;
    color: #0b657e;
  }

  .task-icon :global(img.app-icon) { transform: scale(1.45); }

  .task-title {
    min-width: 120px;
    flex: 1;
    overflow: hidden;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 22px;
    font-weight: 600;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .duration-editor {
    display: flex;
    flex: 0 0 auto;
    align-items: center;
    gap: 9px;
  }

  .number-field {
    position: relative;
    display: block;
    width: 91px;
    height: 48px;
  }

  .duration-editor input {
    width: 91px;
    height: 48px;
    padding: 4px 8px 4px 11px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 20px;
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
    font-size: 18px;
  }

  .priority-editor { flex: 0 0 130px; }

  .priority-editor select {
    width: 100%;
    height: 48px;
    padding: 0 12px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 19px;
    cursor: pointer;
  }

  .remove-btn {
    display: grid;
    width: 31px;
    height: 45px;
    flex: 0 0 31px;
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
