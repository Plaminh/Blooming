<script lang="ts">
  import type { ActivePlantPresentation } from "../../types/presentation";
  import {
    PLANT_ATLAS,
    clampPlantFrameIndex,
    plantSheetTransform,
    plantSource,
  } from "../../model/plants";

  type Props = {
    plant: ActivePlantPresentation;
    class?: string;
  };

  let { plant, class: className = "" }: Props = $props();

  const scale = PLANT_ATLAS.displayHeight / PLANT_ATLAS.cellHeight;
  const displayWidth = PLANT_ATLAS.cellWidth * scale;

  let frame = $derived(clampPlantFrameIndex(plant.frameIndex));
  let source = $derived(plantSource(plant.species));
  let sheetTransform = $derived(plantSheetTransform(frame, scale));
</script>

<div
  class="plant {className}"
  data-species={plant.species}
  data-frame={frame}
  aria-hidden="true"
  style:--sheet-w="{PLANT_ATLAS.sheetWidth}px"
  style:--sheet-h="{PLANT_ATLAS.sheetHeight}px"
  style:--display-w="{displayWidth}px"
  style:--display-h="{PLANT_ATLAS.displayHeight}px"
>
  <div class="viewport" style:overflow="hidden">
    <img
      class="sheet"
      src={source}
      alt=""
      width={PLANT_ATLAS.sheetWidth}
      height={PLANT_ATLAS.sheetHeight}
      style:transform={sheetTransform}
    />
  </div>
</div>

<style>
  .plant,
  .viewport {
    width: var(--display-w);
    height: var(--display-h);
  }

  .plant {
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
