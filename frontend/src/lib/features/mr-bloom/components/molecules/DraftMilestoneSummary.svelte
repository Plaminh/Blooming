<script lang="ts">
  import type { Milestone } from '../../stores/mrBloomStore';
  import TargetDateLabel from '$lib/features/goals/components/atoms/TargetDateLabel.svelte';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { milestone }: { milestone: Milestone } = $props();
</script>

<article class="draft-milestone-summary">
  <div class="milestone-copy">
    <strong>{milestone.title}</strong>
    <TargetDateLabel date={milestone.targetDate} />
  </div>
  <div class="milestone-actions">
    <button aria-label="Edit {milestone.title}"><AppIcon name="pencil" scale={1.15} /></button>
    <button aria-label="Remove {milestone.title}"><AppIcon name="close" scale={1.2} /></button>
  </div>
</article>

<style>
  .draft-milestone-summary {
    display: flex;
    width: 100%;
    height: 84px;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 9px 10px 9px 20px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
  }

  .milestone-copy {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 6px;
  }

  .milestone-copy strong {
    overflow: hidden;
    color: #06459a;
    font-family: var(--bloom-body-font);
    font-size: 23px;
    font-weight: 600;
    line-height: 1.1;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .milestone-copy :global(.target-date) { font-size: 18px; }

  .milestone-actions {
    display: flex;
    flex: 0 0 auto;
    gap: 8px;
  }

  button {
    display: grid;
    width: 54px;
    height: 54px;
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
