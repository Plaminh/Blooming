<script lang="ts">
  import type { StudyStatus } from '../../types';

  let { day, state }: { day: number; state: StudyStatus } = $props();
</script>

<div class="calendar-day-cell {state}" aria-label={state !== 'empty' ? `Day ${day}, ${state}` : undefined}>
  {#if state !== 'empty'}
    <span class="day-number">{day}</span>
  {/if}
</div>

<style>
  .calendar-day-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 4px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 500;
  }

  .calendar-day-cell.empty {
    visibility: hidden;
  }

  .calendar-day-cell.studied {
    background-color: var(--bloom-task-completed-bg);
    color: var(--bloom-text-dark-blue);
  }

  .calendar-day-cell.no-record {
    background-color: var(--color-surface);
    color: var(--bloom-text-dark-blue);
  }

  .calendar-day-cell.inactive {
    background-color: var(--bloom-surface-dark-cream);
    color: var(--bloom-text-muted-blue);
  }
</style>
