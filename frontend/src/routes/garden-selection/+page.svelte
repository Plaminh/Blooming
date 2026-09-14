<script lang="ts">
  import DesktopTitleBar from '$lib/shared/components/organisms/DesktopTitleBar.svelte';
  import GardenSelectionContent from '$lib/features/garden-selection/components/organisms/GardenSelectionContent.svelte';
</script>

<svelte:head>
  <title>Blooming - Choose Your Plant</title>
</svelte:head>

<div class="garden-selection-page">
  <DesktopTitleBar />
  
  <main class="page-content">
    <GardenSelectionContent />
  </main>
</div>

<style>
  :global(body) {
    background-color: #fbfaf5; /* Cream background */
    margin: 0;
    padding: 0;
  }

  .garden-selection-page {
    display: flex;
    flex-direction: column;
    width: 100vw;
    height: 100vh;
    box-sizing: border-box;
    /* Cyan outer frame */
    border: 8px solid #29b9ce;
    overflow: hidden;
  }

  .page-content {
    flex: 1;
    display: flex;
    justify-content: center;
    position: relative;
    overflow-y: auto;
  }
</style>
