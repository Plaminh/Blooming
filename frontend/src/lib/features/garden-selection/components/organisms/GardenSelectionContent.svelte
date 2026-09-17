<script lang="ts">
  import { GardenSelectionViewModel } from "../../model/state.svelte";
  import CurrencyBalance from "../molecules/CurrencyBalance.svelte";
  import PixelHeading from "../atoms/PixelHeading.svelte";
  import PlantPreviewArea from "./PlantPreviewArea.svelte";
  import PlantIdentity from "../molecules/PlantIdentity.svelte";
  import CarouselControls from "../molecules/CarouselControls.svelte";
  import ActionPanel from "./ActionPanel.svelte";

  let vm = new GardenSelectionViewModel();
</script>

<div class="garden-selection-content">
  <div class="top-bar">
    <CurrencyBalance leaves={vm.leavesBalance} water={vm.waterBalance} />
  </div>

  <div class="main-content">
    <PixelHeading
      title="CHOOSE YOUR PLANT"
      subtitle="Pick a companion to grow with you."
    />

    {#if vm.syncWarning}<p role="status">{vm.syncWarning}</p>{/if}

    {#if vm.loading}
      <div class="loading">Loading garden...</div>
    {:else if vm.error}
      <div class="error">{vm.error}</div>
    {:else if vm.selectedPlant}
      <CarouselControls
        hasPrevious={vm.hasPrevious}
        hasNext={vm.hasNext}
        onPrevious={() => vm.previous()}
        onNext={() => vm.next()}
      >
        <div class="carousel-center">
          {#if vm.selectedFrame !== undefined}<PlantPreviewArea
              species={vm.selectedPlant.species}
              frameIndex={vm.selectedFrame}
            />{/if}
          <PlantIdentity
            name={vm.selectedPlant.name}
            description={vm.selectedPlant.description}
          />
        </div>
      </CarouselControls>

      <ActionPanel
        cost={vm.selectedPlant.unlockCost}
        isUnlocked={vm.isSelectedPlantUnlocked}
        isSelected={vm.selectedPlant.id === vm.activePlantId}
        canUnlock={vm.canUnlockSelectedPlant}
        canWater={vm.waterBalance >= 1}
        vitality={vm.vitality}
        onUnlock={() => vm.unlockSelectedPlant()}
        onSelect={() => vm.selectCurrentPlant()}
        onWater={() => vm.waterSelectedPlant()}
      />
    {/if}
  </div>
</div>

<style>
  .garden-selection-content {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    height: 100%;
    box-sizing: border-box;
  }

  .top-bar {
    position: absolute;
    top: 7px;
    right: 10px;
    z-index: 10;
  }

  .main-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    max-width: 720px;
    margin-top: 17px;
  }

  .carousel-center {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 390px;
  }

  .loading,
  .error {
    margin-top: 50px;
    font-family: var(--bloom-body-font);
    font-size: 16px;
  }
  .error {
    color: #d32f2f;
  }
</style>
