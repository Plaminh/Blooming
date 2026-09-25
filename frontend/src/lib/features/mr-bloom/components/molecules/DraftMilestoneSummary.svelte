<script lang="ts">
  import { mrBloomStore, type Milestone } from '../../stores/mrBloomStore';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { milestone }: { milestone: Milestone } = $props();
  const id = $derived(milestone.id ?? '');
</script>

<article class="draft-milestone-summary">
  <input
    class="title-input"
    aria-label="Milestone title"
    value={milestone.title}
    oninput={(event) => mrBloomStore.updateMilestone(id, { title: event.currentTarget.value })}
  />
  <div class="milestone-details">
    <label class="date-field">
      <span>Date</span>
      <input
        class="date-input"
        aria-label={`Target date for ${milestone.title}`}
        type="date"
        value={milestone.targetDate}
        oninput={(event) => mrBloomStore.updateMilestone(id, { targetDate: event.currentTarget.value })}
      />
    </label>
    <label class="outcome-field">
      <span>Expected outcome</span>
      <input
        class="outcome-input"
        aria-label={`Expected outcome for ${milestone.title}`}
        placeholder="Describe the result"
        value={milestone.expectedOutcome ?? ''}
        oninput={(event) => mrBloomStore.updateMilestone(id, { expectedOutcome: event.currentTarget.value || null })}
      />
    </label>
    <button class="remove-button" type="button" aria-label="Remove {milestone.title}" onclick={() => mrBloomStore.removeMilestone(id)}>
      <AppIcon name="close" size="control" />
    </button>
  </div>
</article>

<style>
  .draft-milestone-summary {
    display: flex;
    width: 100%;
    min-width: 0;
    flex-direction: column;
    gap: 5px;
    padding: 7px 9px 8px 11px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
  }

  .milestone-details {
    display: flex;
    min-width: 0;
    align-items: end;
    gap: 8px;
  }

  label { display: flex; min-width: 0; flex-direction: column; gap: 1px; color: #47728f; font-family: var(--bloom-body-font); font-size: 11px; }
  .date-field { width: 122px; flex: 0 0 122px; }
  .outcome-field { flex: 1; }
  .title-input, .date-input, .outcome-input { width:100%; min-width:0; border:0; border-bottom:1px solid transparent; background:transparent; color:#06459a; font:inherit; }
  .title-input { font-size:16px; font-weight:600; }
  .date-input, .outcome-input { height: 22px; font-size:13px; }
  .title-input:focus, .date-input:focus, .outcome-input:focus { border-bottom-color:#00aeea; outline:none; }

  .remove-button {
    display: grid;
    width: 28px;
    height: 28px;
    flex: 0 0 28px;
    padding: 0;
    place-items: center;
    border: 1px solid #c9c3b8;
    border-radius: 4px;
    background: transparent;
    color: #52788c;
    cursor: pointer;
  }

  .remove-button:hover { background: #fff0eb; color: #b13939; }
  .remove-button:focus-visible { outline: 2px solid #00aeea; outline-offset: 2px; }
</style>
