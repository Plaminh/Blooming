<script lang="ts">
  import { mrBloomStore } from '../../stores/mrBloomStore';
  import TimelineHourLabel from '$lib/features/today/components/atoms/TimelineHourLabel.svelte';
  import TimelineTaskSummary from '../molecules/TimelineTaskSummary.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import DraftReviewHeader from './DraftReviewHeader.svelte';

  function hm(value: string, timezone: string) {
    return new Intl.DateTimeFormat([], { hour: '2-digit', minute: '2-digit', hour12: false,
      timeZone: timezone }).format(new Date(value));
  }
  const entries = $derived(($mrBloomStore.preview?.blocks ?? []).map(block => {
    const minutes = Math.max(0, Math.round((new Date(block.planned_end_at).getTime() - new Date(block.planned_start_at).getTime()) / 60000));
    return {
      id: block.id,
      type: block.block_type.toLowerCase() === 'task' ? 'task' as const : block.block_type.toLowerCase() === 'buffer' ? 'buffer' as const : 'break' as const,
      title: block.title ?? (block.block_type === 'BUFFER' ? 'Buffer' : 'Break'),
      startTime: hm(block.planned_start_at, $mrBloomStore.preview?.timezone ?? 'UTC'),
      endTime: hm(block.planned_end_at, $mrBloomStore.preview?.timezone ?? 'UTC'),
      durationLabel: `${minutes} min`, taskId: block.draft_task_id ?? undefined
    };
  }));
</script>

<div class="timeline-draft-preview">
  {#if $mrBloomStore.preview}
    <DraftReviewHeader title="TIMELINE PREVIEW" subtitle="This is the scheduler result that will be saved to Today." />
    <div class="content">
      {#if $mrBloomStore.error}<p class="error" role="alert">{$mrBloomStore.error}</p>{/if}
      <div class="timeline-container">
        <span class="timeline-rail" aria-hidden="true"></span>
        {#each entries as entry, index (entry.id)}
          <div class="timeline-row">
            <div class="time-anchor"><TimelineHourLabel hour={entry.startTime} kind={index === 0 ? 'active' : entry.type === 'buffer' ? 'small' : 'upcoming'} /></div>
            <div class="card-column"><TimelineTaskSummary {entry} selected={index === 0} /></div>
          </div>
        {/each}
      </div>
    </div>
    <DraftReviewActionBar
      secondaryLabel="BACK TO TASKS" onSecondary={() => mrBloomStore.backToTasks()}
      primaryLabel={$mrBloomStore.needsReplace ? "REPLACE TODAY PLAN" : "SAVE TO TODAY"}
      iconSize="control" onPrimary={() => mrBloomStore.saveToday($mrBloomStore.needsReplace)}
      disabled={$mrBloomStore.isSavePending || $mrBloomStore.isDraftMutationPending || $mrBloomStore.isPreviewPending}
      balanced
    />
  {/if}
</div>

<style>
  .timeline-draft-preview { display:flex; width:100%; height:100%; min-width:0; min-height:0; flex-direction:column; }
  .content { min-height:0; flex:1; padding:10px 40px 0 14px; overflow-y:auto; }
  .error { color:#b13939; }
  .timeline-container { --timeline-hour-column-width:88px; --timeline-marker-offset:61px; position:relative; display:flex; min-width:0; flex-direction:column; }
  .timeline-rail { position:absolute; top:37px; bottom:30px; left:calc(var(--timeline-marker-offset) + 4px); z-index:0; width:4px; border-radius:2px; background:#9caab1; }
  .timeline-row { position:relative; min-height:61px; margin-bottom:7px; }
  .time-anchor { position:absolute; top:18px; left:0; z-index:2; width:var(--timeline-hour-column-width); height:24px; }
  .card-column { min-width:0; margin-left:var(--timeline-hour-column-width); }
</style>
