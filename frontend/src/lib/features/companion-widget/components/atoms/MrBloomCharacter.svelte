<script lang="ts">
  import { onMount } from "svelte";
  import type { CompanionWidgetKind } from "../../types/presentation";
  import {
    MR_BLOOM_ATLAS,
    MR_BLOOM_FRAME_SEQUENCE,
    atlasCellForKind,
    atlasSheetTransform,
  } from "../../model/atlas";

  type Props = {
    kind: CompanionWidgetKind;
    class?: string;
  };

  let { kind, class: className = "" }: Props = $props();

  const displayHeight = 110;
  const scale = displayHeight / MR_BLOOM_ATLAS.cellHeight;
  const displayWidth = MR_BLOOM_ATLAS.cellWidth * scale;

  let sequenceIndex = $state(0);
  let reduceMotion = $state(false);
  let frameSequence = $derived(MR_BLOOM_FRAME_SEQUENCE[kind]);
  let cell = $derived(atlasCellForKind(kind, sequenceIndex));
  let sheetTransform = $derived(atlasSheetTransform(cell, scale));

  onMount(() => {
    if (!window.matchMedia) return;

    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const updatePreference = () => {
      reduceMotion = query.matches;
    };

    updatePreference();
    query.addEventListener("change", updatePreference);

    return () => {
      query.removeEventListener("change", updatePreference);
    };
  });

  $effect(() => {
    kind;
    const frozen = reduceMotion;
    sequenceIndex = 0;

    if (frozen || frameSequence.length <= 1) return;

    const timer = window.setInterval(() => {
      sequenceIndex = (sequenceIndex + 1) % frameSequence.length;
    }, MR_BLOOM_ATLAS.frameIntervalMs);

    return () => {
      window.clearInterval(timer);
    };
  });
</script>

<div
  class="character {className}"
  aria-hidden="true"
  data-kind={kind}
  data-frame={cell.col}
  data-sequence-index={sequenceIndex}
  data-row={cell.row}
  data-col={cell.col}
  style:--sheet-w="{MR_BLOOM_ATLAS.sheetWidth}px"
  style:--sheet-h="{MR_BLOOM_ATLAS.sheetHeight}px"
  style:--display-w="{displayWidth}px"
  style:--display-h="{displayHeight}px"
>
  <div class="viewport" style:overflow="hidden">
    <img
      class="sheet"
      src={MR_BLOOM_ATLAS.src}
      alt=""
      width={MR_BLOOM_ATLAS.sheetWidth}
      height={MR_BLOOM_ATLAS.sheetHeight}
      style:transform={sheetTransform}
    />
  </div>
</div>

<style>
  .character {
    width: var(--display-w);
    height: var(--display-h);
    position: relative;
    pointer-events: none;
  }

  .viewport {
    position: absolute;
    left: 0;
    bottom: 0;
    width: var(--display-w);
    height: var(--display-h);
    overflow: hidden;
  }

  .sheet {
    display: block;
    width: var(--sheet-w);
    height: var(--sheet-h);
    max-width: none;
    transform-origin: top left;
    image-rendering: crisp-edges;
    image-rendering: pixelated;
  }
</style>
