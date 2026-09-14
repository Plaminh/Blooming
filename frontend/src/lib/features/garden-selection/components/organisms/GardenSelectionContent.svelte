<script lang="ts">
  import { GardenSelectionViewModel } from '../../model/state.svelte';
  import { INITIAL_GARDEN_STATE } from '../../model/fixtures';
  
  import CurrencyBalance from '../molecules/CurrencyBalance.svelte';
  import PixelHeading from '../atoms/PixelHeading.svelte';
  import PlantPreviewArea from './PlantPreviewArea.svelte';
  import PlantIdentity from '../molecules/PlantIdentity.svelte';
  import CarouselControls from '../molecules/CarouselControls.svelte';
  import UnlockPanel from './UnlockPanel.svelte';

  let vm = new GardenSelectionViewModel(INITIAL_GARDEN_STATE.plants, INITIAL_GARDEN_STATE.session);
</script>

<div class="garden-selection-content">
  <div class="top-bar">
    <CurrencyBalance balance={vm.currencyBalance} />
  </div>

  <div class="main-content">
    <PixelHeading 
      title="CHOOSE YOUR PLANT" 
      subtitle="Pick a companion to grow with you." 
    />

    {#if vm.selectedPlant}
      <CarouselControls 
        hasPrevious={vm.hasPrevious} 
        hasNext={vm.hasNext} 
        onPrevious={() => vm.previous()} 
        onNext={() => vm.next()}
      >
        <div class="carousel-center">
          <PlantPreviewArea species={vm.selectedPlant.species} />
          <PlantIdentity 
            name={vm.selectedPlant.name} 
            description={vm.selectedPlant.description} 
          />
        </div>
      </CarouselControls>

      <UnlockPanel 
        cost={vm.selectedPlant.unlockCost}
        isUnlocked={vm.isSelectedPlantUnlocked}
        canUnlock={vm.canUnlockSelectedPlant}
        onUnlock={() => vm.unlockSelectedPlant()}
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
    top: 40px;
    right: 48px;
    z-index: 10;
  }
  
  .main-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    max-width: 900px;
    margin-top: 80px;
  }

  .carousel-center {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 500px;
  }
</style>
