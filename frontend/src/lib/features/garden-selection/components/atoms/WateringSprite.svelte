<script lang="ts">
  import { onMount } from "svelte";
  import SpriteRenderer from "$lib/shared/components/atoms/SpriteRenderer.svelte";
  import { WATERING_ATLAS } from "$lib/features/companion-widget/model/plants";

  let { onComplete }: { onComplete: () => void } = $props();
  let frameIndex = $state(0);

  onMount(() => {
    let finished = false;
    const finish = () => {
      if (finished) return;
      finished = true;
      onComplete();
    };
    const timer = window.setInterval(() => {
      if (frameIndex >= WATERING_ATLAS.frameCount - 1) {
        window.clearInterval(timer);
        finish();
        return;
      }
      frameIndex += 1;
    }, WATERING_ATLAS.frameDurationMs);
    return () => window.clearInterval(timer);
  });
</script>

<div class="watering-sprite" data-frame={frameIndex} aria-label="Watering plant">
  <SpriteRenderer
    src={WATERING_ATLAS.src}
    sheetWidth={WATERING_ATLAS.sheetWidth}
    sheetHeight={WATERING_ATLAS.sheetHeight}
    columns={WATERING_ATLAS.columns}
    rows={WATERING_ATLAS.rows}
    {frameIndex}
    displayHeight={WATERING_ATLAS.displayHeight}
  />
</div>

<style>
  .watering-sprite {
    height: 165px;
    display: flex;
    align-items: flex-end;
    justify-content: center;
  }
</style>
