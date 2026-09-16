<script lang="ts">
  import GardenSelectionDialog from '$lib/features/garden-selection/components/organisms/GardenSelectionDialog.svelte';
  let gardenOpen = $state(false);
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
    <img class="sky" src="/assets/widget/backgrounds/default-sky.png" alt="" />
    <img class="bushes" src="/assets/widget/backgrounds/background-bushes.png" alt="" />
    <span class="flower f1"></span><span class="flower f2"></span><span class="flower f3"></span>
    <span class="flower f4"></span><span class="flower f5"></span><span class="flower f6"></span>
  </div>
  <footer class="garden-footer">
    <strong>UNLOCKED PLANTS</strong>
    <span>1 / 5</span>
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
    container-type: inline-size;
    min-height: 0;
    overflow: hidden;
    background: var(--bloom-garden-sky);
  }
  .garden-scene img { position: absolute; image-rendering: pixelated; }
  .garden-scene .sky {
    inset: 0;
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
    object-position: center bottom;
  }
  .bushes {
    inset: 0;
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
    object-position: center bottom;
  }
  /* Flower pixel-art colors: intentionally hardcoded — these are exact design values for the decorative garden animation and cannot be semantically tokenized without changing the visual output. */
  .flower { position: absolute; bottom: 12px; width: 6px; height: 22px; background: #2a9561; }
  .flower::before { content: ''; position: absolute; top: 0; left: -5px; width: 16px; height: 9px; background: #ff77a8; box-shadow: inset 5px 0 #ffd9a2, inset -5px 0 #ff8db8; }
  .f1 { left: 16%; }.f2 { left: 31%; }.f3 { left: 47%; }.f4 { left: 62%; }.f5 { left: 78%; }.f6 { left: 91%; }
  .garden-footer { display: flex; align-items: center; gap: 7px; padding: 0 12px; font-family: var(--bloom-body-font); font-size: 15px; color: #064798; }
  .garden-footer span:last-child { margin-left: auto; }
</style>
