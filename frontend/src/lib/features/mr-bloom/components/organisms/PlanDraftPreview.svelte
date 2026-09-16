<script lang="ts">
  import { mrBloomStore, type RoadmapDraft } from '../../stores/mrBloomStore';
  import DraftMilestoneSummary from '../molecules/DraftMilestoneSummary.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import DraftReviewHeader from './DraftReviewHeader.svelte';
  import DraftAddButton from '../molecules/DraftAddButton.svelte';
  import RoadmapNode from '$lib/features/goals/components/atoms/RoadmapNode.svelte';
  import TargetDateLabel from '$lib/features/goals/components/atoms/TargetDateLabel.svelte';

  const draft = $derived($mrBloomStore.activeDraft as RoadmapDraft);
</script>

<div class="plan-draft-preview">
  {#if draft?.type === 'roadmap'}
    <DraftReviewHeader title="ROADMAP DRAFT" />

    <div class="content">
      <div class="goal-summary-row">
        <div class="goal-copy">
          <strong>{draft.goalTitle}</strong>
          <span>{draft.goalDescription}</span>
        </div>
        <div class="target-date-box">
          <span>Target date</span>
          <TargetDateLabel date={draft.targetDate} />
        </div>
      </div>

      <div class="milestones-section">
        <div class="roadmap-timeline">
          {#each draft.milestones as milestone, index (milestone.id)}
            <div class="timeline-row">
              <div class="node-column">
                <RoadmapNode
                  number={index + 1}
                  status="Not started"
                  isLast={index === draft.milestones.length - 1}
                  variant="draft"
                />
              </div>
              <DraftMilestoneSummary {milestone} />
            </div>
          {/each}
        </div>

        <DraftAddButton label="ADD MILESTONE" variant="milestone" />
      </div>
    </div>

    <DraftReviewActionBar
      primaryLabel="SAVE TO GOALS"
      onPrimary={() => mrBloomStore.acceptDraft("Great! I've saved that roadmap to your Goals.")}
      balanced
    />
  {/if}
</div>

<style>
  .plan-draft-preview {
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
    gap: 9px;
    padding: 8px 12px 0;
    overflow-y: auto;
  }

  .goal-summary-row {
    display: flex;
    min-width: 0;
    height: 64px;
    flex: 0 0 64px;
    align-items: stretch;
    gap: 13px;
  }

  .goal-copy {
    display: flex;
    min-width: 0;
    flex: 1;
    flex-direction: column;
    justify-content: center;
    gap: 4px;
    padding: 7px 10px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
    color: #075b9d;
    font-family: var(--bloom-body-font);
  }

  .goal-copy strong {
    overflow: hidden;
    color: #06459a;
    font-size: 18px;
    font-weight: 600;
    line-height: 1.15;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .goal-copy span {
    overflow: hidden;
    font-size: 14px;
    line-height: 1.2;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .target-date-box {
    display: flex;
    width: 145px;
    flex: 0 0 145px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
    color: #075b9d;
    font-family: var(--bloom-body-font);
    font-size: 14px;
  }

  .target-date-box :global(.target-date) { font-size: 14px; }

  .milestones-section {
    display: flex;
    flex-direction: column;
  }

  .roadmap-timeline {
    display: flex;
    flex-direction: column;
  }

  .timeline-row {
    display: flex;
    min-width: 0;
    height: 70px;
    align-items: flex-start;
    gap: 13px;
  }

  .node-column {
    display: flex;
    width: 48px;
    height: 70px;
    flex: 0 0 48px;
  }
</style>
