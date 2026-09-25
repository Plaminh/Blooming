<script lang="ts">
  import { mrBloomStore, type RoadmapDraft } from '../../stores/mrBloomStore';
  import DraftMilestoneSummary from '../molecules/DraftMilestoneSummary.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import DraftReviewHeader from './DraftReviewHeader.svelte';
  import DraftAddButton from '../molecules/DraftAddButton.svelte';
  import { goto } from '$app/navigation';

  const draft = $derived($mrBloomStore.activeDraft as RoadmapDraft);
  const assumptions = $derived.by(() => {
    const seen = new Set<string>();
    return $mrBloomStore.assumptions.filter(assumption => {
      const key = `${assumption.kind}:${assumption.text.trim().toLowerCase()}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  });
  
  let saving = $state(false);
  let saveError = $state<string | null>(null);
  
  async function handleSaveToGoals() {
    if (!draft || draft.type !== 'roadmap') return;
    saving = true;
    saveError = null;
    
    try {
      if (await mrBloomStore.saveRoadmap()) {
        goto('/goals');
      } else {
        saveError = $mrBloomStore.error ?? 'Failed to save goal.';
      }
    } catch (err) {
      saveError = err instanceof Error ? err.message : 'Failed to save goal.';
    } finally {
      saving = false;
    }
  }
</script>

<div class="plan-draft-preview">
  {#if draft?.type === 'roadmap'}
    <DraftReviewHeader
      title="ROADMAP DRAFT"
      subtitle="Review your roadmap before saving it to Goals."
    />

    <div class="content">
      {#if saveError}
        <div class="error-message">{saveError}</div>
      {/if}
      <div class="goal-summary-row">
        <label class="goal-title-field">
          <span>Goal title</span>
          <input aria-label="Goal title" value={draft.goalTitle} oninput={(event) => mrBloomStore.updateRoadmap({ goalTitle: event.currentTarget.value })} />
        </label>
        <label class="target-date-box">
          <span>Target date</span>
          <input aria-label="Goal target date" type="date" value={draft.targetDate} oninput={(event) => mrBloomStore.updateRoadmap({ targetDate: event.currentTarget.value })} />
        </label>
      </div>
      {#if draft.goalDescription}
        <label class="goal-description-field">
          <span>Description</span>
          <input aria-label="Goal description" value={draft.goalDescription} oninput={(event) => mrBloomStore.updateRoadmap({ goalDescription: event.currentTarget.value })} />
        </label>
      {/if}

      {#if assumptions.length}
        <section class="assumptions" aria-label="Roadmap assumptions">
          <strong>Assumptions</strong>
          <ul>
            {#each assumptions as assumption (assumption.id)}
              <li>{assumption.text}</li>
            {/each}
          </ul>
        </section>
      {/if}

      <div class="milestones-section">
        <div class="roadmap-timeline">
          {#each draft.milestones as milestone, index (milestone.id ?? index)}
            <div class="timeline-row">
              <div class="node-column">
                <span class="milestone-number">{index + 1}</span>
                {#if index < draft.milestones.length - 1}<span class="connector" aria-hidden="true"></span>{/if}
              </div>
              <DraftMilestoneSummary {milestone} />
            </div>
          {/each}
        </div>

        <DraftAddButton label="ADD MILESTONE" variant="milestone" disabled={draft.milestones.length >= 12} onclick={() => mrBloomStore.addMilestone()} />
      </div>
    </div>

    <DraftReviewActionBar
      primaryLabel={saving ? "SAVING..." : "SAVE TO GOALS"}
      onPrimary={handleSaveToGoals}
      disabled={saving}
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
    gap: 8px;
    padding: 7px 12px 0;
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
    min-height: 54px;
    align-items: stretch;
    gap: 10px;
  }

  .goal-title-field, .goal-description-field, .target-date-box {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 2px;
    padding: 6px 10px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
    color: #075b9d;
    font-family: var(--bloom-body-font);
  }
  .goal-title-field { flex: 1; }
  .goal-description-field { flex: 0 0 auto; }

  .goal-title-field span, .goal-description-field span, .target-date-box span { color: #47728f; font-size: 11px; }
  .goal-title-field input, .goal-description-field input, .target-date-box input { width:100%; min-width:0; border:0; border-bottom:1px solid transparent; background:transparent; color:inherit; font:inherit; }
  .goal-title-field input { font-size:17px; font-weight:600; }
  .goal-title-field input:focus, .goal-description-field input:focus, .target-date-box input:focus { border-bottom-color:#00aeea; outline:none; }

  .target-date-box {
    display: flex;
    width: 142px;
    flex: 0 0 142px;
    justify-content: center;
  }

  .target-date-box :global(.target-date) { font-size: 14px; }

  .milestones-section {
    display: flex;
    flex-direction: column;
    gap: 7px;
  }

  .roadmap-timeline {
    display: flex;
    flex-direction: column;
  }

  .timeline-row {
    display: flex;
    min-width: 0;
    min-height: 76px;
    align-items: flex-start;
    gap: 8px;
  }

  .node-column {
    display: flex;
    width: 34px;
    min-height: 76px;
    flex: 0 0 34px;
    align-self: stretch;
    flex-direction: column;
    align-items: center;
  }

  .milestone-number {
    display: grid;
    width: 32px;
    height: 32px;
    flex: 0 0 32px;
    place-items: center;
    border: 1px solid #697f86;
    border-radius: 50%;
    background: #90a5aa;
    color: white;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    font-weight: 700;
  }

  .connector { width: 2px; flex: 1; min-height: 12px; background: #b0c0c2; }

  .assumptions {
    padding: 7px 10px;
    border: 1px solid #e1c56d;
    border-radius: 5px;
    background: #fff9df;
    color: #684f0b;
    font-family: var(--bloom-body-font);
    font-size: 13px;
  }
  .assumptions ul { margin: 3px 0 0; padding-left: 18px; }
</style>
