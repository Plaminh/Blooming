<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import StatusBadge from '$lib/shared/components/atoms/StatusBadge.svelte';
  import type { PlanHistoryEntry } from '$lib/api/endpoints/statistics';

  let { entry, onNavigate }: {
    entry: PlanHistoryEntry;
    onNavigate: (id: string) => void;
  } = $props();
</script>

<tr class="plan-history-row">
  <td class="date-cell">{entry.dateLabel}</td>
  <td class="name-cell">{entry.planName}</td>
  <td class="tasks-cell">{entry.completedTasks} / {entry.totalTasks}</td>
  <td class="status-cell">
    <StatusBadge status={entry.status} variant="pill" />
  </td>
  <td class="action-cell">
    <button class="navigate-btn" aria-label="View plan details" onclick={() => onNavigate(entry.id)}>
      <AppIcon name="chevron-right" size="task-type" />
    </button>
  </td>
</tr>

<style>
  .plan-history-row {
    border-bottom: 1px solid var(--bloom-border-subtle);
  }

  .plan-history-row:last-child {
    border-bottom: none;
  }

  td {
    padding: 16px 8px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    color: var(--bloom-text-dark-blue);
  }

  .date-cell {
    width: 15%;
    font-weight: 500;
  }

  .name-cell {
    width: 45%;
    font-weight: 500;
  }

  .tasks-cell {
    width: 15%;
    color: var(--bloom-text-muted-blue);
  }

  .status-cell {
    width: 20%;
  }

  .action-cell {
    width: 5%;
    text-align: right;
  }

  .navigate-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    border-radius: 4px;
    color: var(--bloom-text-muted-blue);
    cursor: pointer;
  }

  .navigate-btn:hover {
    background: var(--bloom-surface-cream-alt);
    color: var(--bloom-text-dark-blue);
  }
  
  .navigate-btn:focus-visible {
    outline: 2px solid var(--bloom-focus);
  }
</style>
