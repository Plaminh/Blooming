<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
</script>

<section class="panel garden" aria-labelledby="garden-heading">
  <header class="panel-strip">
    <img src="/assets/widget/icons/leaf-icon.png" alt="" />
    <h2 id="garden-heading">YOUR GARDEN</h2>
  </header>
  <div class="garden-scene" aria-hidden="true">
    <img class="sky" src="/assets/widget/backgrounds/default-sky.png" alt="" />
    <img class="bushes" src="/assets/widget/backgrounds/background-bushes.png" alt="" />
    <span class="flower f1"></span><span class="flower f2"></span><span class="flower f3"></span>
    <span class="flower f4"></span><span class="flower f5"></span><span class="flower f6"></span>
    <span class="ground"></span>
  </div>
  <footer class="garden-footer">
    <AppIcon name="sprout" scale={0.72} />
    <strong>UNLOCKED PLANTS</strong>
    <span>1 / 5</span>
  </footer>
</section>

<style>
  .panel {
    min-height: 0;
    overflow: hidden;
    border: 1px solid #20a3be;
    border-radius: 5px;
    background: #fffbf2;
    color: #064b91;
    display: grid;
    grid-template-rows: 37px 1fr 55px;
  }
  .panel-strip {
    display: flex;
    height: 37px;
    align-items: center;
    gap: 9px;
    padding: 0 12px;
    background: linear-gradient(#3998ad, #24859f);
    color: #f1fbf7;
  }
  .panel-strip img { width: 26px; height: 27px; object-fit: contain; image-rendering: pixelated; }
  h2 {
    flex: 1;
    margin: 0;
    font-family: var(--bloom-body-font);
    font-size: 17px;
    font-weight: 700;
    line-height: 1;
  }
  .garden-scene { position: relative; min-height: 0; overflow: hidden; border-bottom: 5px solid #bfb8a9; background: #6fcdf5; }
  .garden-scene img { position: absolute; max-width: none; height: auto; image-rendering: pixelated; }
  .sky { left: 0; bottom: -10px; width: 100%; }
  .bushes { left: -50%; bottom: -69px; width: 200%; }
  .ground { position: absolute; inset: auto 0 0; height: 10px; background: #f5d18a; border-top: 3px solid #196d54; }
  .flower { position: absolute; bottom: 12px; width: 6px; height: 22px; background: #2a9561; }
  .flower::before { content: ''; position: absolute; top: 0; left: -5px; width: 16px; height: 9px; background: #ff77a8; box-shadow: inset 5px 0 #ffd9a2, inset -5px 0 #ff8db8; }
  .f1 { left: 16%; }.f2 { left: 31%; }.f3 { left: 47%; }.f4 { left: 62%; }.f5 { left: 78%; }.f6 { left: 91%; }
  .garden-footer { display: flex; align-items: center; gap: 7px; padding: 0 12px; font-family: var(--bloom-body-font); font-size: 15px; color: #064798; }
  .garden-footer span:last-child { margin-left: auto; }
</style>
