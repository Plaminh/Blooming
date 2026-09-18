<script lang="ts">
  import { mrBloomStore } from '../../stores/mrBloomStore';
  import ActionButton from '../atoms/ActionButton.svelte';
  import type { IconSize } from '$lib/shared/components/atoms/AppIcon.svelte';

  let {
    primaryLabel,
    onPrimary,
    secondaryLabel = 'DISCARD',
    onSecondary,
    balanced = false,
    iconSize,
    disabled = false
  }: {
    primaryLabel: string;
    onPrimary: () => void;
    secondaryLabel?: string;
    onSecondary?: () => void;
    balanced?: boolean;
    iconSize?: IconSize;
    disabled?: boolean;
  } = $props();

  const handleSecondary = () => onSecondary ? onSecondary() : mrBloomStore.discardDraft();
</script>

<footer class="draft-review-action-bar" class:balanced>
  <ActionButton
    label={secondaryLabel}
    variant={secondaryLabel === 'DISCARD' ? 'danger' : 'secondary'}
    {disabled}
    onclick={handleSecondary}
  />
  <ActionButton label={primaryLabel} variant="primary" icon="play" {iconSize} {disabled} onclick={onPrimary} />
</footer>

<style>
  .draft-review-action-bar {
    display: grid;
    min-height: 88px;
    flex: 0 0 88px;
    grid-template-columns: 34% minmax(0, 1fr);
    align-items: start;
    gap: 10px;
    padding: 10px 12px 18px;
  }

  .draft-review-action-bar.balanced {
    grid-template-columns: 39% minmax(0, 1fr);
    min-height: 88px;
    flex-basis: 88px;
    padding: 10px 12px 18px;
  }

  .draft-review-action-bar.balanced :global(.action-button) { height: 54px; }
</style>
