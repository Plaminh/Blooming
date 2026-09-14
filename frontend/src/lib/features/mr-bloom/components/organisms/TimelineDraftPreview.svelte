<script lang="ts">
  import { mrBloomStore, type TimelineDraft, type TodayDraft, type TimelineEntry } from '../../stores/mrBloomStore';
  import DraftReviewHeader from './DraftReviewHeader.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import TimelineMarker from '../atoms/TimelineMarker.svelte';
  import TimelineHourLabel from '../molecules/TimelineHourLabel.svelte';
  import TimelineTaskSummary from '../molecules/TimelineTaskSummary.svelte';
  
  let todayDraft = $derived($mrBloomStore.activeDraft?.type === 'today' ? $mrBloomStore.activeDraft as TodayDraft : null);
  
  let draft = $derived.by(() => {
    if (!todayDraft) return null;
    
    const todayTasks = todayDraft.tasks;
    const entries: TimelineEntry[] = [];
    let currentHour = parseInt(todayDraft.availability.start.split(':')[0]);
    let currentMin = parseInt(todayDraft.availability.start.split(':')[1]);
    
    function addTime(mins: number) {
      const newMin = (currentMin + mins) % 60;
      const hoursToAdd = Math.floor((currentMin + mins) / 60);
      const endHour = currentHour + hoursToAdd;
      const endMin = newMin;
      
      const startStr = `${currentHour.toString().padStart(2, '0')}:${currentMin.toString().padStart(2, '0')}`;
      const endStr = `${endHour.toString().padStart(2, '0')}:${endMin.toString().padStart(2, '0')}`;
      
      currentHour = endHour;
      currentMin = endMin;
      
      return { startStr, endStr };
    }
    
    todayTasks.forEach((task, i) => {
      const { startStr, endStr } = addTime(task.durationMin);
      entries.push({
        id: `te-${i}`,
        type: 'task',
        title: task.title,
        startTime: startStr,
        endTime: endStr,
        durationLabel: `${task.durationMin} min`,
        taskId: task.id,
        icon: task.icon
      });
      
      if (i < todayTasks.length - 1) {
         const breakTime = addTime(15);
         entries.push({
           id: `tb-${i}`,
           type: 'break',
           title: 'Take a breather',
           startTime: breakTime.startStr,
           endTime: breakTime.endStr,
           durationLabel: '15 min'
         });
      }
    });
    
    return {
      type: 'timeline',
      entries
    } as TimelineDraft;
  });
  
  function handleBack() {
    mrBloomStore.backToTasks();
  }
  
  function handleAccept() {
    mrBloomStore.acceptDraft("Excellent. I've locked in your schedule for today.");
  }
</script>

<div class="timeline-draft-preview">
  {#if draft && draft.type === 'timeline'}
    <DraftReviewHeader 
      type="TIMELINE" 
      title="Your Day" 
      subtitle="Here's a proposed schedule including buffer times." 
    />
    
    <div class="content">
      <div class="timeline-container">
        <div class="timeline-rail"></div>
        
        {#each draft.entries as entry, i}
          <div class="timeline-row">
            <TimelineHourLabel hour={entry.startTime} />
            <TimelineMarker active={i === 0} />
            <div class="entry-content">
              <TimelineTaskSummary {entry} />
            </div>
          </div>
        {/each}
        
        <!-- End of day marker -->
        {#if draft.entries.length > 0}
          <div class="timeline-row end-row">
            <TimelineHourLabel hour={draft.entries[draft.entries.length - 1].endTime} />
            <TimelineMarker />
            <div class="entry-content"></div>
          </div>
        {/if}
      </div>
    </div>
    
    <DraftReviewActionBar 
      primaryLabel="Save to Today" 
      onPrimary={handleAccept} 
      secondaryLabel="Back to tasks"
      onSecondary={handleBack}
    />
  {/if}
</div>

<style>
  .timeline-draft-preview {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
  }
  
  .content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
  }
  
  .timeline-container {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }
  
  .timeline-rail {
    position: absolute;
    left: 65px; /* 48px label + 17px spacing to center of marker */
    top: 6px;
    bottom: 6px;
    width: 2px;
    background: #cfc9b9;
    z-index: 1;
  }
  
  .timeline-row {
    display: flex;
    gap: 16px;
    min-height: 48px;
  }
  
  .timeline-row.end-row {
    min-height: 24px;
  }
  
  .entry-content {
    flex: 1;
    padding-bottom: 24px;
  }
  
  .end-row .entry-content {
    padding-bottom: 0;
  }
  
  /* Reset padding for global timeline markers alignment */
  :global(.timeline-row > .timeline-marker) {
    margin-top: 4px;
  }
</style>
