<script lang="ts">
  import PlantSprite from '$lib/shared/sprites/PlantSprite.svelte';
  import PanelHeading from "../atoms/PanelHeading.svelte";
</script>

<div class="live-draft">
  <div class="header">
    <PanelHeading>LIVE DRAFT</PanelHeading>
  </div>

  <div class="content">
    <div class="plant-container">
      <div class="sparkles">
        <span class="sparkle s1"></span>
        <span class="sparkle s2"></span>
        <span class="sparkle s3"></span>
        <span class="sparkle s4"></span>
        <span class="sparkle s5"></span>
      </div>
      <PlantSprite plant={{ species: "monstera", frameIndex: 0, scale: 1.35 }} />
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
    padding: 15px 21px 0;
    flex-shrink: 0;
  }

  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px;
    text-align: center;
    transform: translateY(-46px);
  }

  .plant-container {
    position: relative;
    width: 188px;
    height: 188px;
    display: grid;
    place-items: end center;
    margin-bottom: 14px;
  }

  .sparkles {
    position: absolute;
    inset: 0;
    pointer-events: none;
    transform: translateY(-10px);
  }

  .sparkle {
    position: absolute;
    z-index: 1;
    width: 7px;
    height: 17px;
    background: #8cc75b;
    box-shadow: 5px 5px 0 #8cc75b;
  }

  .s1 {
    top: 10%;
    left: 20%;
    transform: rotate(-20deg);
  }
  .s2 {
    top: 0%;
    left: 50%;
  }
  .s3 {
    top: 15%;
    right: 15%;
    transform: rotate(20deg);
  }
  .s4 {
    top: 45%;
    left: 10%;
    transform: rotate(-45deg);
  }
  .s5 {
    top: 40%;
    right: 5%;
    transform: rotate(45deg);
  }

  .heading {
    font-family: var(--bloom-display-font);
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.085em;
    color: #071f66;
    margin: 0 0 7px 0;
  }

  .description {
    font-family: var(--bloom-body-font);
    font-size: 22px;
    color: #1a6595;
    line-height: 1.35;
    margin: 0;
  }
</style>
