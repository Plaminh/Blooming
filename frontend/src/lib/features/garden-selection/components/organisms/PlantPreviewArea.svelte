<script lang="ts">
  import SpriteRenderer from '$lib/shared/components/atoms/SpriteRenderer.svelte';
  import { PLANT_ATLAS, PLANT_SOURCES } from '$lib/features/companion-widget/model/plants';
  import type { PlantSpecies } from '../../types';
  
  let { species }: { species: PlantSpecies } = $props();
  
  let src = $derived(PLANT_SOURCES[species]);
</script>

<div class="plant-preview-area">
  <div class="artwork-wrapper">
    <SpriteRenderer
      {src}
      sheetWidth={PLANT_ATLAS.sheetWidth}
      sheetHeight={PLANT_ATLAS.sheetHeight}
      columns={PLANT_ATLAS.columns}
      rows={PLANT_ATLAS.rows}
      frameIndex={0}
      displayHeight={360}
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
    margin: 24px 0;
  }
  .artwork-wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .shadow {
    width: 240px;
    height: 32px;
    background: #d8d3c5; /* A slightly darker cream for the shadow */
    border-radius: 50%;
    margin-top: -32px;
    z-index: -1;
  }
</style>
