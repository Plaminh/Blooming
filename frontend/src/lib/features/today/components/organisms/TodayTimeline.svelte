<script lang="ts">
  import PageHeading from '$lib/shared/components/atoms/PageHeading.svelte';
  import type { Task } from '$lib/features/today/types';
  import type { PendingTask } from '$lib/api/types';
  import { createTimelineGeometry, timeInTimezone } from '$lib/features/today/timeline';
  import { onMount } from 'svelte';
  import DateNavigation from '../atoms/DateNavigation.svelte';
  import TimelineHourLabel from '../atoms/TimelineHourLabel.svelte';
  import TimelineCard from '../molecules/TimelineCard.svelte';

  let { tasks, currentDate, isToday = true, planTimezone = 'UTC', now, selectedTaskId, isLoading = false, loadError = null, waitingTasks = [], onSelect, onDateChange }: {
    tasks: Task[];
    currentDate: Date;
    isToday?: boolean;
    planTimezone?: string;
    now?: Date;
    selectedTaskId: string;
    isLoading?: boolean;
    loadError?: string | null;
    waitingTasks?: PendingTask[];
    onSelect: (id: string) => void;
    onDateChange: (offset: number) => void;
  } = $props();

  const formattedDate = $derived(
    currentDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
  );
  let clock = $state(new Date());
  const effectiveNow = $derived(now ?? clock);
  const currentTime = $derived(isToday ? timeInTimezone(effectiveNow, planTimezone) : undefined);
  const geometry = $derived(createTimelineGeometry(tasks, currentTime));

  onMount(() => {
    if (now) return;
    const timer = window.setInterval(() => (clock = new Date()), 60_000);
    return () => window.clearInterval(timer);
  });
</script>

<section class="timeline-container" aria-labelledby="today-heading">
  <header class="timeline-header">
    <div>
      <PageHeading id="today-heading" title="TODAY" />
      <p>{formattedDate}</p>
    </div>
    <DateNavigation {currentDate} {isToday} {onDateChange} />
  </header>

  <div class="timeline-view">
    <div class="timeline-canvas" data-range={`${geometry.start}-${geometry.end}`} style:min-height={`${geometry.height}px`}>
      <span class="axis-line" aria-hidden="true"></span>
      {#each geometry.hours as hour}
        <div class="marker" data-hour={hour} style:top={`${geometry.topFor(hour) - 12}px`}>
          <TimelineHourLabel {hour} kind="small" />
        </div>
      {/each}

      {#if currentTime}
        <div
          class="current-time-marker"
          data-testid="current-time-marker"
          aria-label={`Current time ${currentTime}`}
          style:top={`${geometry.topFor(currentTime)}px`}
        ><span></span></div>
      {/if}

      {#if isLoading}
        <p class="empty-state">Loading schedule...</p>
      {:else if loadError}
        <p class="empty-state" style="color: var(--bloom-error)">{loadError}</p>
      {:else if tasks.length}
        {#each tasks as task (task.id)}
          <TimelineCard {task} top={geometry.topFor(task.startTime)} selected={selectedTaskId === task.id} {onSelect} />
        {/each}
      {:else if waitingTasks.length}
        <div class="empty-state waiting" data-testid="waiting-tasks">
          <p>{waitingTasks.length} {waitingTasks.length === 1 ? 'task is' : 'tasks are'} waiting for this day. Plan them with Mr. Bloom:</p>
          <ul>
            {#each waitingTasks as item, index (`${item.task_id ?? item.title}-${index}`)}
              <li>{item.reason === 'RECURRING' ? '↻ ' : ''}{item.title}</li>
            {/each}
          </ul>
        </div>
      {:else}
        <p class="empty-state">No tasks scheduled for this day.</p>
      {/if}
    </div>
  </div>
</section>

<style>
  .timeline-container {
    display: flex;
    min-height: 0;
    flex: 1;
    flex-direction: column;
    padding: 16px 2px 0 25px;
  }
  .timeline-header {
    display: flex;
    height: 82px;
    flex: 0 0 82px;
    align-items: flex-start;
    justify-content: space-between;
  }
  .timeline-header p {
    margin-top: 1px;
    color: #1374a7;
    font-family: var(--bloom-body-font);
    font-size: 20px;
    line-height: 1.2;
  }
  .timeline-header :global(.date-navigator) { margin-top: 8px; }
  .timeline-view {
    min-height: 0;
    flex: 1;
    overflow-y: auto;
  }
  .timeline-canvas {
    position: relative;
    height: 100%;
  }
  .axis-line {
    position: absolute;
    top: 8px;
    bottom: 8px;
    left: 91px;
    width: 4px;
    background: #b9c1c8;
  }
  .marker { position: absolute; left: 0; z-index: 2; }
  .current-time-marker {
    position: absolute;
    right: 12px;
    left: 85px;
    z-index: 4;
    height: 2px;
    background: #24abe7;
    transform: translateY(-1px);
    pointer-events: none;
  }
  .current-time-marker span {
    position: absolute;
    top: 50%;
    left: 0;
    width: 14px;
    height: 14px;
    border: 3px solid #24abe7;
    border-radius: 50%;
    background: #fffdf5;
    transform: translate(-50%, -50%);
  }
  .empty-state {
    position: absolute;
    inset: 110px 20px 0 132px;
    display: grid;
    place-items: center;
    color: #4c7894;
    font-family: var(--bloom-body-font);
    font-size: 17px;
  }
  .empty-state.waiting {
    align-content: center;
    place-items: center start;
    gap: 6px;
  }
  .empty-state.waiting p { margin: 0; }
  .empty-state.waiting ul { margin: 0; padding-left: 20px; }
</style>
