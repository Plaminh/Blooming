<script lang="ts">
  import { mrBloomStore, type TodayDraft } from '../../stores/mrBloomStore';
  import DraftTaskSummary from '../molecules/DraftTaskSummary.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import DraftReviewHeader from './DraftReviewHeader.svelte';
  import DraftAddButton from '../molecules/DraftAddButton.svelte';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let draft = $derived($mrBloomStore.activeDraft as TodayDraft);
</script>

<div class="today-draft-preview">
  {#if draft?.type === 'today'}
    <DraftReviewHeader
      title="TODAY DRAFT"
      subtitle="Review the extracted tasks before generating your timeline."
    />

    <div class="content">
      <div class="availability-bar">
        <span class="availability-icon"><AppIcon name="calendar" size="detail" /></span>
        <span>Available · {draft.availability.start} – {draft.availability.end} · {draft.availability.totalHours} hours</span>
      </div>

      <div class="tasks-list">
        {#each draft.tasks as task (task.id)}
          <DraftTaskSummary {task} />
        {/each}
      </div>

      <DraftAddButton label="ADD TASK" variant="task" disabled={true} />
      <div class="content-divider" aria-hidden="true"></div>
    </div>

    <DraftReviewActionBar
      primaryLabel="GENERATE TIMELINE"
      iconSize="control"
      onPrimary={() => mrBloomStore.generateTimeline()}
    />
  {/if}
</div>

<style>
  .today-draft-preview {
    display: flex;
    width: 100%;
    height: 100%;
    min-width: 0;
    min-height: 0;
    flex-direction: column;
  }

  .content {
    display: flex;
    min-height: 0;
    flex: 1;
    flex-direction: column;
    gap: 10px;
    padding: 10px 12px 0;
    overflow-y: auto;
  }

  .availability-bar {
    display: flex;
    min-height: 50px;
    flex: 0 0 50px;
    align-items: center;
    gap: 12px;
    padding: 6px 12px;
    border: 2px solid #70c7ed;
    border-radius: 5px;
    background: var(--bloom-task-active-bg);
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 16px;
  }

  .availability-icon {
    display: grid;
    width: var(--bloom-icon-detail);
    height: var(--bloom-icon-detail);
    flex: 0 0 var(--bloom-icon-detail);
    place-items: center;
    color: #0b506e;
  }

  .tasks-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .content-divider {
    width: 100%;
    margin-top: -6px;
    border-top: 2px solid #c8cfca;
  }
</style>
