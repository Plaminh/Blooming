<script lang="ts">
  import { mrBloomStore, type TimelineDraft, type TimelineEntry, type TodayDraft } from '../../stores/mrBloomStore';
  import { addMinutesToTime, formatTimelineDuration, minutesBetween } from '$lib/features/today/timeline';
  import TimelineHourLabel from '$lib/features/today/components/atoms/TimelineHourLabel.svelte';
  import TimelineTaskSummary from '../molecules/TimelineTaskSummary.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import DraftReviewHeader from './DraftReviewHeader.svelte';

  const todayDraft = $derived($mrBloomStore.activeDraft?.type === 'today' ? $mrBloomStore.activeDraft as TodayDraft : null);

  const draft = $derived.by<TimelineDraft | null>(() => {
    if (!todayDraft) return null;

    const entries: TimelineEntry[] = [];
    let cursor = todayDraft.availability.start;

    todayDraft.tasks.forEach((task, index) => {
      const endTime = addMinutesToTime(cursor, task.durationMin);
      entries.push({
        id: `timeline-${task.id}`,
        type: 'task',
        title: task.title,
        startTime: cursor,
        endTime,
        durationLabel: formatTimelineDuration(task.durationMin),
        taskId: task.id,
        icon: task.icon
      });
      cursor = endTime;

      if (index === 0) {
        const breakEnd = addMinutesToTime(cursor, 30);
        entries.push({
          id: 'timeline-break',
          type: 'break',
          title: 'Break',
          startTime: cursor,
          endTime: breakEnd,
          durationLabel: '30 min',
          icon: 'sprout'
        });
        cursor = breakEnd;
      }

      if (index === 1) {
        const lunchEnd = addMinutesToTime(cursor, 60);
        entries.push({
          id: 'timeline-lunch',
          type: 'break',
          title: 'Lunch',
          startTime: cursor,
          endTime: lunchEnd,
          durationLabel: '1 hour',
          icon: 'break'
        });
        cursor = lunchEnd;
      }
    });

    const remainingMinutes = minutesBetween(cursor, todayDraft.availability.end);
    if (remainingMinutes > 0) {
      entries.push({
        id: 'timeline-buffer',
        type: 'buffer',
        title: `Buffer · ${remainingMinutes} min`,
        startTime: cursor,
        endTime: todayDraft.availability.end,
        durationLabel: `${remainingMinutes} min`
      });
    }

    return { type: 'timeline', entries };
  });
</script>

<div class="timeline-draft-preview">
  {#if draft}
    <DraftReviewHeader title="TIMELINE DRAFT" subtitle="Review the schedule before saving it to Today." />

    <div class="content">
      <div class="timeline-container">
        <span class="timeline-rail" aria-hidden="true"></span>
        {#each draft.entries as entry, index (entry.id)}
          <div class="timeline-row">
            <div class="time-anchor">
              <TimelineHourLabel
                hour={entry.startTime}
                kind={index === 0 ? 'active' : entry.type === 'buffer' ? 'small' : 'upcoming'}
              />
            </div>
            <div class="card-column">
              <TimelineTaskSummary {entry} selected={index === 0 || entry.title === 'Lunch'} />
            </div>
          </div>
        {/each}
      </div>
    </div>

    <DraftReviewActionBar
      secondaryLabel="BACK TO TASKS"
      onSecondary={() => mrBloomStore.backToTasks()}
      primaryLabel="SAVE TO TODAY"
      iconSize="control"
      onPrimary={() => mrBloomStore.acceptDraft("Excellent. I've locked in your schedule for today.")}
      balanced
    />
  {/if}
</div>

<style>
  .timeline-draft-preview {
    display: flex;
    width: 100%;
    height: 100%;
    min-width: 0;
    min-height: 0;
    flex-direction: column;
  }

  .content {
    min-height: 0;
    flex: 1;
    padding: 10px 40px 0 14px;
    overflow-y: auto;
  }

  .timeline-container {
    --timeline-hour-column-width: 88px;
    --timeline-hour-label-width: 48px;
    --timeline-marker-offset: 61px;
    position: relative;
    display: flex;
    min-width: 0;
    flex-direction: column;
  }

  .timeline-rail {
    position: absolute;
    top: 37px;
    bottom: 95px;
    left: calc(var(--timeline-marker-offset) + 4px);
    z-index: 0;
    width: 4px;
    border-radius: 2px;
    background: #9caab1;
  }

  .timeline-row {
    position: relative;
    min-height: 61px;
    margin-bottom: 7px;
  }

  .timeline-row:last-child { margin-bottom: 0; }

  .timeline-row:last-child::before {
    content: '';
    position: absolute;
    top: -39px;
    bottom: 30px;
    left: calc(var(--timeline-marker-offset) + 4px);
    width: 4px;
    background: repeating-linear-gradient(to bottom, #9caab1 0 8px, transparent 8px 15px);
  }

  .time-anchor {
    position: absolute;
    top: 18px;
    left: 0;
    z-index: 2;
    width: var(--timeline-hour-column-width);
    height: 24px;
  }

  .card-column {
    min-width: 0;
    margin-left: var(--timeline-hour-column-width);
  }
</style>
