<script lang="ts">
  let {
    src,
    sheetWidth,
    sheetHeight,
    columns,
    rows,
    frameIndex,
    displayHeight,
    class: className = ''
  }: {
    src: string;
    sheetWidth: number;
    sheetHeight: number;
    columns: number;
    rows: number;
    frameIndex: number;
    displayHeight: number;
    class?: string;
  } = $props();

  let cellWidth = $derived(sheetWidth / columns);
  let cellHeight = $derived(sheetHeight / rows);
  let scale = $derived(displayHeight / cellHeight);
  let displayWidth = $derived(cellWidth * scale);

  let safeFrame = $derived(Math.min((columns * rows) - 1, Math.max(0, Math.trunc(frameIndex))));
  let col = $derived(safeFrame % columns);
  let row = $derived(Math.floor(safeFrame / columns));

  let sheetTransform = $derived(`scale(${scale}) translate(${-col * cellWidth}px, ${-row * cellHeight}px)`);
</script>

<div
  class="sprite-renderer {className}"
  aria-hidden="true"
  style:--sheet-w="{sheetWidth}px"
  style:--sheet-h="{sheetHeight}px"
  style:--display-w="{displayWidth}px"
  style:--display-h="{displayHeight}px"
>
  <div class="viewport">
    <img
      class="sheet"
      {src}
      alt=""
      width={sheetWidth}
      height={sheetHeight}
      style:transform={sheetTransform}
    />
  </div>
</div>

<style>
  .sprite-renderer,
  .viewport {
    width: var(--display-w);
    height: var(--display-h);
  }

  .sprite-renderer {
    pointer-events: none;
  }

  .viewport {
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
