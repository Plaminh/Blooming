<script lang="ts">
  import SpriteRenderer from "$lib/shared/components/atoms/SpriteRenderer.svelte";
  import {
    PLANT_ATLAS,
    PLANT_SOURCES,
  } from "$lib/features/companion-widget/model/plants";
  import type { PlantSpecies } from "../../types";
  import type { GrowthStage } from "$lib/api/types";
  import { getPlantFrame } from "$lib/features/garden/utils/spriteMapper";
  import WateringSprite from "../atoms/WateringSprite.svelte";

  let {
    species,
    growthStage,
    vitality,
    watering = false,
    onWateringComplete = () => {},
  }: {
    species: PlantSpecies;
    growthStage: GrowthStage;
    vitality: number;
    watering?: boolean;
    onWateringComplete?: () => void;
  } = $props();

  let src = $derived(PLANT_SOURCES[species]);
  let frameIndex = $derived(getPlantFrame(species, growthStage, vitality));
</script>

<div class="plant-preview-area">
  <div class="artwork-wrapper">
    {#if watering}
      <WateringSprite onComplete={onWateringComplete} />
    {:else}
      <SpriteRenderer
        {src}
        sheetWidth={PLANT_ATLAS.sheetWidth}
        sheetHeight={PLANT_ATLAS.sheetHeight}
        columns={PLANT_ATLAS.columns}
        rows={PLANT_ATLAS.rows}
        {frameIndex}
        displayHeight={165}
        class="plant-sprite"
      />
    {/if}
    <div class="shadow"></div>
  </div>
</div>

<style>
  .plant-preview-area {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 5px 0 2px;
  }
  .artwork-wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .shadow {
    width: 140px;
    height: 18px;
    background: #d8d3c5;
    border-radius: 50%;
    margin-top: -18px;
    z-index: -1;
  }
</style>
