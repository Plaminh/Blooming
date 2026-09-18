<script lang="ts">
  import SpriteRenderer from "$lib/shared/components/atoms/SpriteRenderer.svelte";
  import {
    PLANT_ATLAS,
    PLANT_SOURCES,
  } from "$lib/features/companion-widget/model/plants";
  import type { PlantSpecies } from "../../types";

  let {
    species,
    frameIndex,
    scale = 1,
  }: {
    species: PlantSpecies;
    scale?: number;
    frameIndex: import("$lib/features/companion-widget/types/presentation").PlantFrameIndex;
  } = $props();

  let src = $derived(PLANT_SOURCES[species]);
</script>

<div class="plant-preview-area">
  <div class="artwork-wrapper" style:transform="scale({scale})" style:transform-origin="bottom center">
    <SpriteRenderer
      {src}
      sheetWidth={PLANT_ATLAS.sheetWidth}
      sheetHeight={PLANT_ATLAS.sheetHeight}
      columns={PLANT_ATLAS.columns}
      rows={PLANT_ATLAS.rows}
      {frameIndex}
      displayHeight={190}
      class="plant-sprite"
    />
    <div class="shadow"></div>
  </div>
</div>

<style>
  .plant-preview-area {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 14px 0 4px;
  }
  .artwork-wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .shadow {
    width: 150px;
    height: 20px;
    background: #d8d3c5;
    border-radius: 50%;
    margin-top: -20px;
    z-index: -1;
  }
</style>
