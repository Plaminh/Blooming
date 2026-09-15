<script lang="ts">
  import QuoteCard from '../molecules/QuoteCard.svelte';
</script>

<aside class="brand-panel" aria-label="Blooming introduction">
  <img
    src="/assets/onboarding-setup/backgrounds/onboarding-background.png"
    alt=""
    class="brand-scene"
    width="432"
    height="582"
  />
  <div class="desk-extension" aria-hidden="true"></div>

  <div class="marketing-copy">
    <h1 class="marketing-headline">BLOOMING</h1>
    <p class="marketing-subline">A calmer desktop.<br />A brighter you.</p>
  </div>

  <QuoteCard />
</aside>

<style>
  .brand-panel {
    position: relative;
    min-width: 0;
    overflow: hidden;
    background: #eee4d0;
    box-shadow: inset -2px 0 0 var(--bloom-frame);
  }

  .brand-scene {
    position: absolute;
    top: 0;
    left: 0;
    display: block;
    width: 432px;
    height: 582px;
    max-width: none;
    object-fit: none;
    object-position: top left;
    image-rendering: crisp-edges;
    image-rendering: pixelated;
  }

  .desk-extension {
    position: absolute;
    top: 582px;
    right: 0;
    left: 0;
    height: 36px;
    background:
      linear-gradient(
        to bottom,
        #8d7f73 0 13px,
        #5f6871 13px 18px,
        #a7adb0 18px 23px,
        #c9c5bc 23px 34px,
        #d8cfbf 34px 36px
      );
  }

  .marketing-copy {
    position: absolute;
    z-index: 2;
    top: 48px;
    left: 68px;
  }

  .marketing-headline {
    margin: 0 0 1px;
    color: #083d66;
    font-family: var(--bloom-display-font);
    font-size: 43px;
    font-weight: 900;
    letter-spacing: 0.12em;
    line-height: 1.18;
    text-shadow: 1px 1px 0 rgba(255, 255, 255, 0.36);
  }

  .marketing-subline {
    margin: 0;
    color: #174b70;
    font-family: var(--bloom-body-font);
    font-size: 20px;
    line-height: 1.25;
  }
</style>
