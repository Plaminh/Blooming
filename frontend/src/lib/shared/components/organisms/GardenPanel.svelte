<script lang="ts">
  import GardenSelectionDialog from '$lib/features/garden-selection/components/organisms/GardenSelectionDialog.svelte';
  import { GardenSelectionViewModel } from '$lib/features/garden-selection/model/state.svelte';
  import { gardenUpdates } from '$lib/features/garden-selection/model/gardenUpdates';
  import WidgetSceneBackground from '$lib/features/companion-widget/components/molecules/WidgetSceneBackground.svelte';
  import { desktop } from '$lib/platform/desktopWindow';
  import { onMount } from 'svelte';
  let gardenOpen = $state(false);
  let vm = new GardenSelectionViewModel();

  onMount(() => {
    let first = true;
    let disposed = false;
    let offDesktop = () => {};
    const offGarden = gardenUpdates.subscribe(() => {
      if (first) { first = false; return; }
      void vm.loadState();
    });
    desktop.onScheduleUpdated(() => void vm.loadState()).then((cleanup) => {
      if (disposed) cleanup();
      else offDesktop = cleanup;
    }).catch(() => {});
    return () => {
      disposed = true;
      offGarden();
      offDesktop();
    };
  });
  function openGarden(event: MouseEvent) {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    gardenOpen = true;
  }
</script>

<a class="panel garden" href="/garden-selection" aria-labelledby="garden-heading" onclick={openGarden}>
  <header class="panel-strip">
    <h2 id="garden-heading">YOUR GARDEN</h2>
  </header>
  <div class="garden-scene" aria-hidden="true">
    <WidgetSceneBackground variant="garden" />
  </div>
  <footer class="garden-footer">
    <strong>UNLOCKED PLANTS</strong>
    <span>{vm.unlockedPlants.size} / {vm.plants.length}</span>
  </footer>
</a>

<GardenSelectionDialog open={gardenOpen} onClose={() => { gardenOpen = false; }} />

<style>
  .panel {
    min-height: 0;
    overflow: hidden;
    border: 1px solid var(--bloom-garden-border);
    border-radius: 5px;
    background: var(--bloom-garden-surface);
    color: var(--bloom-text-dark-blue);
    text-decoration: none;
    cursor: pointer;
    display: grid;
    grid-template-rows: 37px minmax(0, 1fr) 55px;
  }
  .garden:focus-visible {
    outline: 3px solid var(--bloom-focus);
    outline-offset: -3px;
  }
  .panel-strip {
    display: flex;
    height: 37px;
    align-items: center;
    gap: 9px;
    padding: 0 12px;
    background: var(--bloom-titlebar-bg);
    color: #f1fbf7;
  }
  h2 {
    flex: 1;
    margin: 0;
    font-family: var(--bloom-body-font);
    font-size: 17px;
    font-weight: 700;
    line-height: 1;
  }
  .garden-scene {
    position: relative;
    container-type: size;
    min-height: 0;
    overflow: hidden;
    background: var(--bloom-garden-sky);
  }
  .garden-footer { display: flex; align-items: center; gap: 7px; padding: 0 12px; font-family: var(--bloom-body-font); font-size: 15px; color: #064798; }
  .garden-footer span:last-child { margin-left: auto; }
</style>
