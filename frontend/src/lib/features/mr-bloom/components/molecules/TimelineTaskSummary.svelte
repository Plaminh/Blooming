<script lang="ts">
  import type { TimelineEntry } from '../../stores/mrBloomStore';
  import AppIcon, { type IconName } from '$lib/shared/components/atoms/AppIcon.svelte';

  let { entry, selected = false }: { entry: TimelineEntry; selected?: boolean } = $props();

  const icon = $derived.by<IconName>(() => {
    if (entry.icon) return entry.icon;
    if (entry.title === 'Lunch') return 'break';
    return entry.type === 'break' ? 'sprout' : 'document';
  });
</script>

<article
  class="timeline-task-summary {entry.type}"
  class:selected
  class:lunch={entry.title === 'Lunch'}
>
  <span class="entry-icon">
    {#if entry.type === 'buffer'}
      <span class="buffer-icon" aria-hidden="true"></span>
    {:else}
      <AppIcon name={icon} scale={2.05} />
    {/if}
  </span>
  <span class="entry-copy">
    <strong>{entry.title}</strong>
    <span>{entry.startTime} – {entry.endTime} ({entry.durationLabel})</span>
  </span>
  {#if entry.type !== 'buffer'}
    <button class="edit-button" aria-label="Edit {entry.title}">
      <AppIcon name="pencil" scale={1.15} />
    </button>
  {/if}
</article>

<style>
  .timeline-task-summary {
    display: flex;
    width: 100%;
    height: 75px;
    align-items: center;
    gap: 14px;
    padding: 8px 10px 8px 14px;
    border: 2px solid #d1cabd;
    border-radius: 5px;
    background: #fffaf0;
    color: #064b91;
  }

  .timeline-task-summary.selected,
  .timeline-task-summary.lunch {
    border-color: #65c4eb;
    background: linear-gradient(90deg, #e4f7ff, #dbf2fc);
  }

  .timeline-task-summary.break:not(.lunch) {
    border-color: #b9d9b3;
    background: #f1faed;
  }

  .timeline-task-summary.buffer {
    border-color: #c9c9c2;
    border-style: dashed;
    background: rgba(255, 253, 247, 0.58);
  }

  .entry-icon {
    display: grid;
    width: 63px;
    height: 55px;
    flex: 0 0 63px;
    place-items: center;
    color: #0b5d7b;
  }

  .entry-icon :global(img.app-icon) { transform: scale(1.4); }
  .break:not(.lunch) .entry-icon { color: #3b9655; }

  .entry-copy {
    display: flex;
    min-width: 0;
    flex: 1;
    flex-direction: column;
    color: #075b9d;
    font-family: var(--bloom-body-font);
    line-height: 1.2;
  }

  .entry-copy strong {
    overflow: hidden;
    color: #06459a;
    font-size: 23px;
    font-weight: 600;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .entry-copy > span { font-size: 17px; }

  .buffer .entry-copy strong { color: #315e83; }
  .buffer .entry-copy > span { color: #547c99; }

  .edit-button {
    display: grid;
    width: 54px;
    height: 54px;
    flex: 0 0 54px;
    padding: 0;
    place-items: center;
    border: 2px solid #c4c2b8;
    border-radius: 5px;
    background: #fffaf0;
    color: #06528c;
    cursor: pointer;
  }

  .edit-button:hover { background: #e2f5fc; }
  .edit-button:focus-visible { outline: 2px solid #00aeea; outline-offset: 2px; }

  .buffer-icon {
    width: 44px;
    height: 44px;
    border: 4px dashed #718d9b;
    border-radius: 50%;
  }
</style>
