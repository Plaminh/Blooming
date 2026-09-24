<script lang="ts">
  import { mrBloomStore, type Milestone } from '../../stores/mrBloomStore';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { milestone }: { milestone: Milestone } = $props();
  const id = $derived(milestone.id ?? '');
</script>

<article class="draft-milestone-summary">
  <div class="milestone-copy">
    <input
      class="title-input"
      aria-label="Milestone title"
      value={milestone.title}
      oninput={(event) => mrBloomStore.updateMilestone(id, { title: event.currentTarget.value })}
    />
    <input
      class="date-input"
      aria-label={`Target date for ${milestone.title}`}
      type="date"
      value={milestone.targetDate}
      oninput={(event) => mrBloomStore.updateMilestone(id, { targetDate: event.currentTarget.value })}
    />
    <input
      class="outcome-input"
      aria-label={`Expected outcome for ${milestone.title}`}
      placeholder="Expected outcome"
      value={milestone.expectedOutcome ?? ''}
      oninput={(event) => mrBloomStore.updateMilestone(id, { expectedOutcome: event.currentTarget.value || null })}
    />
  </div>
  <div class="milestone-actions">
    <button type="button" aria-label="Remove {milestone.title}" onclick={() => mrBloomStore.removeMilestone(id)}><AppIcon name="close" scale={1.2} /></button>
  </div>
</article>

<style>
  .draft-milestone-summary {
    display: flex;
    width: 100%;
    min-height: 76px;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 7px 9px 7px 12px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
  }

  .milestone-copy {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 4px;
  }

  .title-input, .date-input, .outcome-input { min-width:0; border:0; border-bottom:1px solid transparent; background:transparent; color:#06459a; font:inherit; }
  .title-input { font-size:17px; font-weight:600; }
  .outcome-input { font-size:13px; }
  .title-input:focus, .date-input:focus, .outcome-input:focus { border-bottom-color:#00aeea; outline:none; }

  .milestone-copy :global(.target-date) { font-size: 14px; }

  .milestone-actions {
    display: flex;
    flex: 0 0 auto;
    gap: 6px;
  }

  button {
    display: grid;
    width: 42px;
    height: 42px;
    padding: 0;
    place-items: center;
    border: 2px solid #c4c2b8;
    border-radius: 5px;
    background: #fffaf0;
    color: #06528c;
    cursor: pointer;
  }

  button:hover { background: #e2f5fc; }
  button:focus-visible { outline: 2px solid #00aeea; outline-offset: 2px; }
</style>
