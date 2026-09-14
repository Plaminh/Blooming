<script lang="ts">
  import type { Task } from '$lib/features/today/types';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import TaskStatusBadge from '../atoms/TaskStatusBadge.svelte';

  let { task, selected, onSelect }: { task: Task; selected: boolean; onSelect: (id: string) => void } = $props();
</script>

<button
  class="task-card {task.status} card-{task.id}"
  class:selected
  onclick={() => onSelect(task.id)}
  aria-pressed={selected}
>
  <span class="task-icon"><AppIcon name={task.iconRef} scale={0.88} /></span>
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
    height: 82px;
    align-items: center;
    padding: 0 20px 0 22px;
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
    background: linear-gradient(90deg, #e0f6ff, #d8f2ff);
  }
  .task-card.completed {
    border-color: #8ed9aa;
    background: linear-gradient(90deg, #eef8e9, #edf8ec);
  }
  .task-card.upcoming { background: linear-gradient(90deg, #fffdf7, #faf6ed); }
  .card-1 { top: 8px; }
  .card-2 { top: 100px; }
  .card-3 { top: 192px; }
  .card-4 { top: 290px; }

  .task-icon {
    display: grid;
    width: 74px;
    place-items: center start;
    flex: 0 0 74px;
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
    font-size: 20px;
    font-weight: 700;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .task-copy > span { font-size: 17px; }
  .task-card :global(.badge) { margin-left: 16px; }
</style>
