<script lang="ts">
  import PlantSprite from '$lib/features/companion-widget/components/atoms/PlantSprite.svelte';
</script>

<div class="live-draft">
  <div class="header">
    <h2 class="title">LIVE DRAFT</h2>
  </div>
  
  <div class="content">
    <div class="plant-container">
      <div class="sparkles">
        <img src="/assets/widget/icons/sparkle-icon.png" class="sparkle s1" alt="" />
        <img src="/assets/widget/icons/sparkle-icon.png" class="sparkle s2" alt="" />
        <img src="/assets/widget/icons/sparkle-icon.png" class="sparkle s3" alt="" />
        <img src="/assets/widget/icons/sparkle-icon.png" class="sparkle s4" alt="" />
        <img src="/assets/widget/icons/sparkle-icon.png" class="sparkle s5" alt="" />
      </div>
      <!-- Frame index 2 or 3 for small sprout -->
      <PlantSprite plant={{ species: 'monstera', frameIndex: 3 }} />
    </div>
    
    <h3 class="heading">Your draft will grow here</h3>
    <p class="description">
      As we talk, Mr. Bloom will turn your ideas<br />
      into an editable plan.
    </p>
  </div>
</div>

<style>
  .live-draft {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
  }

  .header {
    padding: 16px 24px;
    border-bottom: 1px solid #cfc9b9;
    flex-shrink: 0;
  }
  
  .title {
    font-family: var(--bloom-header-font, 'Pixelify Sans', sans-serif);
    font-size: 20px;
    color: #064798;
    margin: 0;
    text-transform: uppercase;
  }

  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px;
    text-align: center;
  }

  .plant-container {
    position: relative;
    width: 120px;
    height: 120px;
    display: grid;
    place-items: end center;
    margin-bottom: 24px;
  }

  .plant-container :global(.plant) {
    transform: scale(2);
    transform-origin: bottom center;
  }
  
  .sparkles {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }
  
  .sparkle {
    position: absolute;
    width: 12px;
    height: 12px;
    image-rendering: pixelated;
  }
  
  .s1 { top: 10%; left: 20%; transform: rotate(-20deg); }
  .s2 { top: 0%; left: 50%; }
  .s3 { top: 15%; right: 15%; transform: rotate(20deg); }
  .s4 { top: 45%; left: 10%; transform: rotate(-45deg); }
  .s5 { top: 40%; right: 5%; transform: rotate(45deg); }

  .heading {
    font-family: var(--bloom-header-font, 'Pixelify Sans', sans-serif);
    font-size: 24px;
    color: #064798;
    margin: 0 0 12px 0;
  }

  .description {
    font-family: var(--bloom-body-font);
    font-size: 16px;
    color: #064798;
    line-height: 1.5;
    margin: 0;
  }
</style>
