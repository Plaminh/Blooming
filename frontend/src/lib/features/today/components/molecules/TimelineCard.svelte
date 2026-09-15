<script lang="ts">
  import type { Task } from '$lib/features/today/types';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import TaskStatusBadge from '../atoms/TaskStatusBadge.svelte';

  let { task, selected, top, onSelect }: {
    task: Task;
    selected: boolean;
    top: number;
    onSelect: (id: string) => void;
  } = $props();
</script>

<button
  class="task-card {task.status}"
  class:selected
  style:top={`${top}px`}
  onclick={() => onSelect(task.id)}
  aria-pressed={selected}
>
  <span class="task-icon"><AppIcon name={task.iconRef} size="task-type" /></span>
  <span class="task-copy">
    <strong>{task.title}</strong>
    <span>{task.startTime} – {task.endTime}</span>
  </span>
  <TaskStatusBadge status={task.status} />
</button>

<style>
  .task-card {
    position: absolute;
    left: 110px;
    right: 12px;
    display: flex;
    height: 66px;
    align-items: center;
    padding: 0 14px 0 16px;
    border: 1px solid #c8c9c4;
    border-radius: 5px;
    background: #fffaf0;
    color: #06479a;
    text-align: left;
    cursor: pointer;
  }
  .task-card:focus-visible { outline: 2px solid #00aeea; outline-offset: 2px; }
  .task-card.in-progress,
  .task-card.selected.in-progress {
    border-color: #23bce7;
    background: var(--bloom-task-active-bg);
  }
  .task-card.completed {
    border-color: #8ed9aa;
    background: var(--bloom-task-completed-bg);
  }
  .task-card.upcoming { background: var(--bloom-task-upcoming-bg); }
  .task-icon {
    display: grid;
    width: var(--bloom-icon-task-type-slot);
    place-items: center;
    flex: 0 0 var(--bloom-icon-task-type-slot);
  }
  .task-copy {
    display: flex;
    min-width: 0;
    flex: 1;
    flex-direction: column;
    color: #075a9d;
    font-family: var(--bloom-body-font);
  }
  .task-copy strong {
    overflow: hidden;
    margin-bottom: 1px;
    color: #06429a;
    font-size: 17px;
    font-weight: 700;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .task-copy > span { font-size: 14px; }
  .task-card :global(.badge) { margin-left: 12px; }
</style>
