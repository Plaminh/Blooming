<script lang="ts">
  import { mrBloomStore, type RoadmapDraft } from '../../stores/mrBloomStore';
  import DraftMilestoneSummary from '../molecules/DraftMilestoneSummary.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import DraftReviewHeader from './DraftReviewHeader.svelte';
  import RoadmapNode from '$lib/features/goals/components/atoms/RoadmapNode.svelte';
  import TargetDateLabel from '$lib/features/goals/components/atoms/TargetDateLabel.svelte';

  const draft = $derived($mrBloomStore.activeDraft as RoadmapDraft);
</script>

<div class="plan-draft-preview">
  {#if draft?.type === 'roadmap'}
    <DraftReviewHeader title="ROADMAP DRAFT" />

    <div class="content">
      <div class="goal-summary-row">
        <span class="goal-icon"><img src="/assets/widget/icons/leaf-icon.png" alt="" /></span>
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

        <button class="add-milestone-btn"><span aria-hidden="true">+</span> ADD MILESTONE</button>
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
    gap: 13px;
    padding: 11px 16px 0;
    overflow-y: auto;
  }

  .goal-summary-row {
    display: flex;
    min-width: 0;
    height: 80px;
    flex: 0 0 80px;
    align-items: stretch;
    gap: 13px;
  }

  .goal-icon {
    display: grid;
    width: 55px;
    flex: 0 0 55px;
    place-items: center;
  }

  .goal-icon img {
    width: 55px;
    height: 55px;
    object-fit: contain;
    image-rendering: pixelated;
    transform: scale(1.48);
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
    font-size: 22px;
    font-weight: 600;
    line-height: 1.15;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .goal-copy span {
    overflow: hidden;
    font-size: 16px;
    line-height: 1.2;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .target-date-box {
    display: flex;
    width: 181px;
    flex: 0 0 181px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
    color: #075b9d;
    font-family: var(--bloom-body-font);
    font-size: 17px;
  }

  .target-date-box :global(.target-date) { font-size: 18px; }

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
    height: 94px;
    align-items: flex-start;
    gap: 13px;
  }

  .node-column {
    display: flex;
    width: 55px;
    height: 94px;
    flex: 0 0 55px;
    transform: translateY(5px);
  }

  .add-milestone-btn {
    display: flex;
    width: 270px;
    height: 58px;
    flex: 0 0 58px;
    align-items: center;
    gap: 18px;
    margin-top: 1px;
    padding: 0 22px;
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

  .add-milestone-btn span {
    font-family: var(--bloom-body-font);
    font-size: 39px;
    font-weight: 300;
  }

  .add-milestone-btn:hover { background: #eef8f6; }
  .add-milestone-btn:focus-visible { outline: 2px solid #00aeea; outline-offset: 2px; }
</style>
