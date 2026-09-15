<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    width = 'var(--bloom-app-canvas-width)',
    height = 'var(--bloom-app-canvas-height)',
    label,
    children,
  }: {
    width?: string;
    height?: string;
    label?: string;
    children: Snippet;
  } = $props();
</script>

<div
  class="fixed-canvas-viewport"
  style:--fixed-canvas-width={width}
  style:--fixed-canvas-height={height}
>
  <div class="fixed-canvas-stage">
    <div class="fixed-canvas" aria-label={label}>
      {@render children()}
    </div>
  </div>
</div>

<style>
  .fixed-canvas-viewport {
    --fixed-canvas-scale: min(
      1,
      calc(100vw / var(--fixed-canvas-width)),
      calc(100vh / var(--fixed-canvas-height))
    );

    position: fixed;
    inset: 0;
    display: grid;
    overflow: hidden;
    place-items: center;
    background: var(--bloom-canvas);
  }

  .fixed-canvas-stage {
    position: relative;
    width: calc(var(--fixed-canvas-width) * var(--fixed-canvas-scale));
    height: calc(var(--fixed-canvas-height) * var(--fixed-canvas-scale));
    flex: none;
  }

  .fixed-canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: var(--fixed-canvas-width);
    height: var(--fixed-canvas-height);
    transform: scale(var(--fixed-canvas-scale));
    transform-origin: top left;
  }
</style>
