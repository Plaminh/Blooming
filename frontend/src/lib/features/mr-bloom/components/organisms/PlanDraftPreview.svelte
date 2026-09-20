<script lang="ts">
  import { mrBloomStore, type RoadmapDraft } from '../../stores/mrBloomStore';
  import DraftMilestoneSummary from '../molecules/DraftMilestoneSummary.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import DraftReviewHeader from './DraftReviewHeader.svelte';
  import DraftAddButton from '../molecules/DraftAddButton.svelte';
  import RoadmapNode from '$lib/features/goals/components/atoms/RoadmapNode.svelte';
  import TargetDateLabel from '$lib/features/goals/components/atoms/TargetDateLabel.svelte';
  import { goalsStore } from '$lib/features/goals/stores/goalsStore';
  import { goto } from '$app/navigation';

  const draft = $derived($mrBloomStore.activeDraft as RoadmapDraft);
  
  let saving = $state(false);
  let saveError = $state<string | null>(null);
  
  async function handleSaveToGoals() {
    if (!draft || draft.type !== 'roadmap') return;
    saving = true;
    saveError = null;
    
    try {
      const targetDate = draft.targetDate;
      
      const newGoal = await goalsStore.createGoal({
        title: draft.goalTitle,
        description: draft.goalDescription,
        target_date: targetDate
      });
      
      for (const m of draft.milestones) {
        const dueAt = m.targetDate.includes('T') ? m.targetDate : `${m.targetDate}T00:00:00Z`;
        await goalsStore.addMilestone(newGoal.id, {
          title: m.title,
          due_at: dueAt
        });
      }
      
      mrBloomStore.acceptDraft("Great! I've saved that roadmap to your Goals.");
      goto('/goals');
    } catch (err) {
      // NOTE: The Goals API does not support atomic Goal+Milestone creation.
      // If a milestone fails, the Goal (and prior milestones) will still exist,
      // but the UI will show this error and preserve the draft.
      saveError = err instanceof Error ? err.message : 'Failed to save goal.';
    } finally {
      saving = false;
    }
  }
</script>

<div class="plan-draft-preview">
  {#if draft?.type === 'roadmap'}
    <DraftReviewHeader title="ROADMAP DRAFT" />

    <div class="content">
      {#if saveError}
        <div class="error-message">{saveError}</div>
      {/if}
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
                  status="PENDING"
                  isLast={index === draft.milestones.length - 1}
                  variant="draft"
                />
              </div>
              <DraftMilestoneSummary {milestone} />
            </div>
          {/each}
        </div>

        <DraftAddButton label="ADD MILESTONE" variant="milestone" disabled={true} />
      </div>
    </div>

    <DraftReviewActionBar
      primaryLabel={saving ? "SAVING..." : "SAVE TO GOALS"}
      onPrimary={handleSaveToGoals}
      disabled={saving}
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

  .error-message {
    padding: 12px;
    border-radius: 5px;
    background: #fff0eb;
    color: #b13939;
    border: 1px solid #b75252;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 500;
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
