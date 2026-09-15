<script lang="ts">
  import { mrBloomStore, type TodayDraft } from '../../stores/mrBloomStore';
  import DraftTaskSummary from '../molecules/DraftTaskSummary.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import DraftReviewHeader from './DraftReviewHeader.svelte';
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
        <span class="availability-icon"><AppIcon name="calendar" scale={1.75} /></span>
        <span>Available · {draft.availability.start} – {draft.availability.end} · {draft.availability.totalHours} hours</span>
      </div>

      <div class="tasks-list">
        {#each draft.tasks as task (task.id)}
          <DraftTaskSummary {task} />
        {/each}
      </div>

      <button class="add-task-btn">
        <span aria-hidden="true">+</span>
        ADD TASK
      </button>
      <div class="content-divider" aria-hidden="true"></div>
    </div>

    <DraftReviewActionBar
      primaryLabel="GENERATE TIMELINE"
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
    gap: 18px;
    padding: 15px 14px 0 16px;
    overflow-y: auto;
  }

  .availability-bar {
    display: flex;
    min-height: 62px;
    flex: 0 0 62px;
    align-items: center;
    gap: 18px;
    padding: 8px 17px;
    border: 2px solid #70c7ed;
    border-radius: 5px;
    background: linear-gradient(90deg, #e4f6ff, #d8f1fd);
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 21px;
  }

  .availability-icon {
    display: grid;
    width: 44px;
    height: 44px;
    flex: 0 0 44px;
    place-items: center;
    color: #0b506e;
  }

  .tasks-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .add-task-btn {
    display: flex;
    width: 212px;
    height: 64px;
    flex: 0 0 64px;
    align-items: center;
    gap: 18px;
    padding: 0 24px;
    border: 2px solid #9e9a8f;
    border-radius: 5px;
    background: #fffaf0;
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.055em;
    cursor: pointer;
  }

  .add-task-btn span {
    font-family: var(--bloom-body-font);
    font-size: 39px;
    font-weight: 300;
  }

  .add-task-btn:hover { background: #eef8f6; }
  .add-task-btn:focus-visible { outline: 2px solid #00aeea; outline-offset: 2px; }

  .content-divider {
    width: 100%;
    margin-top: -6px;
    border-top: 2px solid #c8cfca;
  }
</style>
