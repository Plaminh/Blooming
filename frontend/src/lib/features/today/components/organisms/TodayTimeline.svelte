<script lang="ts">
  import PageHeading from '$lib/shared/components/atoms/PageHeading.svelte';
  import type { Task } from '$lib/features/today/types';
  import { minutesBetween } from '$lib/features/today/timeline';
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

  const cardTop = 8;
  const cardHeight = 66;
  const timelineStart = '09:00';
  const hourStep = 70;
  const markerTopOffset = (cardHeight - 24) / 2;
  const timeTop = (time: string) => cardTop + minutesBetween(timelineStart, time) * hourStep / 60;
  const markerDefinitions = [
    { hour: '09:00', kind: 'active' },
    { hour: '10:00', kind: 'completed' },
    { hour: '11:00', kind: 'upcoming' },
    { hour: '12:00', kind: 'upcoming' },
    { hour: '13:00', kind: 'active' },
    { hour: '14:00', kind: 'small' },
    { hour: '15:00', kind: 'small' },
    { hour: '16:00', kind: 'small' }
  ] as const;
  const markers = markerDefinitions.map((marker) => ({
    ...marker,
    top: timeTop(marker.hour) + markerTopOffset
  }));
  const rulerHeight = markers[markers.length - 1].top + 24 + cardTop;
</script>

<section class="timeline-container" aria-labelledby="today-heading">
  <header class="timeline-header">
    <div>
      <PageHeading id="today-heading" title="TODAY" />
      <p>{formattedDate}</p>
    </div>
    <DateNavigation {onDateChange} />
  </header>

  <div class="timeline-view">
    <div class="timeline-canvas" style:min-height={`${rulerHeight}px`}>
      <span class="axis-line" aria-hidden="true"></span>
      {#each markers as marker}
        <div class="marker" style:top={`${marker.top}px`}>
          <TimelineHourLabel hour={marker.hour} kind={marker.kind} />
        </div>
      {/each}

      {#if tasks.length}
        {#each tasks as task (task.id)}
          <TimelineCard {task} top={timeTop(task.startTime)} selected={selectedTaskId === task.id} {onSelect} />
        {/each}
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
    top: 29px;
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
