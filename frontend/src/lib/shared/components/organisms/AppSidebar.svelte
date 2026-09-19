<script lang="ts">
  import PlantSprite from "$lib/features/companion-widget/components/atoms/PlantSprite.svelte";
  import AppIcon from "$lib/shared/components/atoms/AppIcon.svelte";
  import SidebarNavigationItem from "../molecules/SidebarNavigationItem.svelte";
  import { goto } from "$app/navigation";
  import { GardenSelectionViewModel } from "$lib/features/garden-selection/model/state.svelte";

  import { onMount } from "svelte";
  import { desktop } from "$lib/platform/desktopWindow";
  import { gardenUpdates } from "$lib/features/garden-selection/model/gardenUpdates";

  let { activeRoute = "TODAY" }: { activeRoute?: string } = $props();

  let vm = new GardenSelectionViewModel();
  onMount(() => {
    let disposed = false;
    let off = () => {};
    const refresh = setInterval(() => void vm.loadState(), 60000);
    let first = true;
    const offGarden = gardenUpdates.subscribe(() => {
      if (first) { first = false; return; }
      void vm.loadState();
    });
    desktop
      .onScheduleUpdated(() => void vm.loadState())
      .then((cleanup) => {
        if (disposed) cleanup();
        else off = cleanup;
      })
      .catch(() => {
        vm.error = "Garden synchronization unavailable.";
      });
    return () => {
      disposed = true;
      off();
      offGarden();
      clearInterval(refresh);
    };
  });
</script>

<div class="sidebar">
  <nav class="sidebar-nav" aria-label="Primary navigation">
    <SidebarNavigationItem
      label="TODAY"
      icon="today"
      active={activeRoute === "TODAY"}
      onClick={() => goto("/today")}
    />
    <SidebarNavigationItem
      label="GOALS"
      icon="goals"
      active={activeRoute === "GOALS"}
      onClick={() => goto("/goals")}
    />
    <SidebarNavigationItem
      label="MR. BLOOM"
      icon="chat"
      active={activeRoute === "MR. BLOOM"}
      onClick={() => goto("/mr-bloom")}
    />
    <SidebarNavigationItem
      label="STATISTICS"
      icon="statistics"
      active={activeRoute === "STATISTICS"}
      onClick={() => goto("/statistics")}
    />
    <SidebarNavigationItem
      label="SETTINGS"
      icon="settings"
      active={activeRoute === "SETTINGS"}
      onClick={() => goto("/settings")}
    />
  </nav>

  <div class="sidebar-bottom">
    <div class="plant-container">
      {#if vm.activePlantPresentation}
        <PlantSprite plant={vm.activePlantPresentation} />
      {/if}
    </div>
    <div class="counters" aria-label="Garden currency">
      <div class="counter">
        <img
          class="leaf-counter"
          src="/assets/icons/leaf-icon.png"
          alt="Leaves"
        />
        <span>{vm.leavesBalance}</span>
      </div>
      <div class="counter">
        <span class="water-counter"
          ><AppIcon name="water" size="counter-water" label="Water" /></span
        >
        <span>{vm.waterBalance}</span>
      </div>
    </div>
  </div>
</div>

<style>
  .sidebar {
    display: flex;
    min-width: 0;
    height: 100%;
    flex-direction: column;
    justify-content: space-between;
    padding: 45px 9px 0;
    border-right: 1px solid #cfc9b9;
    background: #f4faf6;
  }

  .sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .sidebar-bottom {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-bottom: 18px;
  }

  .plant-container {
    display: grid;
    width: 126px;
    height: 188px;
    place-items: end center;
    margin-bottom: 6px;
    transform: translateX(1px);
  }

  .plant-container :global(.plant) {
    transform: scale(var(--bloom-sidebar-plant-scale));
    transform-origin: bottom center;
  }

  .counters {
    display: flex;
    align-items: center;
    gap: 19px;
    transform: translateX(-5px);
  }

  .counter {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #064798;
    font-family: var(--bloom-body-font);
    font-size: 23px;
    font-weight: 700;
  }

  .leaf-counter {
    width: 44px;
    height: 50px;
    padding: 8px;
    object-fit: contain;
    image-rendering: pixelated;
  }
  .water-counter {
    display: flex;
    width: 30px;
    height: 30px;
    flex: 0 0 30px;
    align-items: center;
    justify-content: center;
  }
</style>
