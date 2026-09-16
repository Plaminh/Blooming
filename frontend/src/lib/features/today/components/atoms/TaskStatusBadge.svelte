<script lang="ts">
  import type { TaskStatus } from '../../types';
  let { status }: { status: TaskStatus } = $props();

  const text: Record<TaskStatus, string> = {
    'in-progress': 'In progress',
    completed: 'Completed',
    upcoming: 'Upcoming'
  };
</script>

<span class="task-status-badge status-{status}">
  {text[status]}
</span>

<style>
  .task-status-badge {
    display: grid;
    min-width: 112px;
    height: 34px;
    place-items: center;
    border-radius: 5px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 500;
    white-space: nowrap;
  }
  .status-completed {
    background: var(--bloom-task-status-completed-bg);
    color: var(--bloom-task-status-completed-text);
  }
  .status-in-progress {
    background: var(--bloom-task-status-in-progress-bg);
    color: var(--bloom-task-status-in-progress-text);
  }
  .status-upcoming {
    background: var(--bloom-task-status-upcoming-bg);
    color: var(--bloom-task-status-upcoming-text);
  }
</style>
