<script lang="ts">
  import GardenSelectionContent from '$lib/features/garden-selection/components/organisms/GardenSelectionContent.svelte';
</script>

<svelte:head>
  <title>Blooming - Choose Your Plant</title>
</svelte:head>

<main class="page-content">
  <GardenSelectionContent />
</main>

<style>
  .page-content {
    display: flex;
    width: 100%;
    height: 100%;
    justify-content: center;
    position: relative;
    overflow: hidden;
    background: var(--bloom-surface-cream);
  }
</style>
