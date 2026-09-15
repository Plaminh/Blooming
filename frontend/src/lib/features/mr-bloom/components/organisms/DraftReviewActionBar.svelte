<script lang="ts">
  import { mrBloomStore } from '../../stores/mrBloomStore';
  import ActionButton from '../atoms/ActionButton.svelte';

  let {
    primaryLabel,
    onPrimary,
    secondaryLabel = 'DISCARD',
    onSecondary,
    balanced = false
  }: {
    primaryLabel: string;
    onPrimary: () => void;
    secondaryLabel?: string;
    onSecondary?: () => void;
    balanced?: boolean;
  } = $props();

  const handleSecondary = () => onSecondary ? onSecondary() : mrBloomStore.discardDraft();
</script>

<footer class="draft-review-action-bar" class:balanced>
  <ActionButton
    label={secondaryLabel}
    variant={secondaryLabel === 'DISCARD' ? 'danger' : 'secondary'}
    onclick={handleSecondary}
  />
  <ActionButton label={primaryLabel} variant="primary" icon="play" onclick={onPrimary} />
</footer>

<style>
  .draft-review-action-bar {
    display: grid;
    min-height: 119px;
    flex: 0 0 119px;
    grid-template-columns: 34% minmax(0, 1fr);
    align-items: start;
    gap: 14px;
    padding: 16px 14px 33px 16px;
  }

  .draft-review-action-bar.balanced {
    grid-template-columns: 39% minmax(0, 1fr);
    min-height: 116px;
    flex-basis: 116px;
    padding: 16px 16px 34px;
  }

  .draft-review-action-bar.balanced :global(.action-button) { height: 66px; }
</style>
