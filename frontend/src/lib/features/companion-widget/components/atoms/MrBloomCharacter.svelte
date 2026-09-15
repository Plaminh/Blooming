<script lang="ts">
  import { onMount } from "svelte";
  import type { CompanionWidgetKind } from "../../types/presentation";
  import {
    MR_BLOOM_ATLAS,
    MR_BLOOM_FRAME_SEQUENCE,
    MR_BLOOM_CHAT_ANIMATIONS,
    type MrBloomChatAnimation,
    atlasCellForKind,
    atlasSheetTransform,
  } from "../../model/atlas";

  type Props = {
    kind?: CompanionWidgetKind;
    animation?: MrBloomChatAnimation;
    displayHeight?: number;
    class?: string;
  };

  let { kind = 'reminders', animation, displayHeight = 110, class: className = "" }: Props = $props();

  const scale = $derived(displayHeight / MR_BLOOM_ATLAS.cellHeight);
  const displayWidth = $derived(MR_BLOOM_ATLAS.cellWidth * scale);

  let sequenceIndex = $state(0);
  let reduceMotion = $state(false);
  let frameSequence = $derived(MR_BLOOM_FRAME_SEQUENCE[kind]);
  let chatAnimation = $derived(animation ? MR_BLOOM_CHAT_ANIMATIONS[animation] : null);
  let cell = $derived(chatAnimation
    ? { row: chatAnimation.row, col: chatAnimation.frames[sequenceIndex % chatAnimation.frames.length].col }
    : atlasCellForKind(kind, sequenceIndex));
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
    const profile = chatAnimation;
    sequenceIndex = 0;

    if (profile) {
      if (frozen) return;
      let frameIndex = 0;
      let timer: number;
      const scheduleFrame = () => {
        timer = window.setTimeout(() => {
          frameIndex = (frameIndex + 1) % profile.frames.length;
          sequenceIndex = frameIndex;
          scheduleFrame();
        }, profile.frames[frameIndex].durationMs);
      };
      scheduleFrame();
      return () => window.clearTimeout(timer);
    }

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
  data-animation={animation}
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
