<script lang="ts">
  import type { Task } from '$lib/features/today/types';
  import DateNavigation from '../atoms/DateNavigation.svelte';
  import TimelineHourLabel from '../atoms/TimelineHourLabel.svelte';
  import TimelineCard from '../molecules/TimelineCard.svelte';

  let { tasks, currentDate, selectedTaskId, onSelect, onDateChange }: {
    tasks: Task[];
    currentDate: Date;
    selectedTaskId: string;
    onSelect: (id: string) => void;
    onDateChange: (offset: number) => void;
  } = $props();

  const formattedDate = $derived(
    currentDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
  );

  const markers = [
    { hour: '09:00', top: 28, kind: 'active' },
    { hour: '10:00', top: 116, kind: 'completed' },
    { hour: '11:00', top: 209, kind: 'upcoming' },
    { hour: '12:00', top: 303, kind: 'upcoming' },
    { hour: '13:00', top: 400, kind: 'active' },
    { hour: '14:00', top: 488, kind: 'small' },
    { hour: '15:00', top: 557, kind: 'small' },
    { hour: '16:00', top: 609, kind: 'small' }
  ] as const;
</script>

<section class="timeline-container" aria-labelledby="today-heading">
  <header class="timeline-header">
    <div>
      <h1 id="today-heading">TODAY</h1>
      <p>{formattedDate}</p>
    </div>
    <DateNavigation {onDateChange} />
  </header>

  <div class="timeline-view">
    <span class="axis-line" aria-hidden="true"></span>
    {#each markers as marker}
      <div class="marker" style:top={`${marker.top}px`}>
        <TimelineHourLabel hour={marker.hour} kind={marker.kind} />
      </div>
    {/each}

    {#if tasks.length}
      {#each tasks as task}
        <TimelineCard {task} selected={selectedTaskId === task.id} {onSelect} />
      {/each}
    {:else}
      <p class="empty-state">No tasks scheduled for this day.</p>
    {/if}
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
  h1 {
    margin: 0;
    color: #063d68;
    font-family: var(--bloom-display-font);
    font-size: 46px;
    font-weight: 900;
    letter-spacing: -0.06em;
    line-height: 1;
    text-shadow: 1px 0 currentColor;
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
    position: relative;
    min-height: 0;
    flex: 1;
  }
  .axis-line {
    position: absolute;
    top: 22px;
    bottom: 14px;
    left: 91px;
    width: 4px;
    background: #b9c1c8;
  }
  .marker { position: absolute; left: 0; z-index: 2; }
  .empty-state {
    position: absolute;
    inset: 110px 20px 0 132px;
    display: grid;
    place-items: center;
    color: #4c7894;
    font-family: var(--bloom-body-font);
    font-size: 17px;
  }
</style>
