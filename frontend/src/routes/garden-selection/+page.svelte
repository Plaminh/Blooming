<script lang="ts">
  import DesktopAppShell from '$lib/shared/components/organisms/DesktopAppShell.svelte';
  import GardenSelectionContent from '$lib/features/garden-selection/components/organisms/GardenSelectionContent.svelte';
</script>

<svelte:head>
  <title>Blooming - Choose Your Plant</title>
</svelte:head>

<DesktopAppShell
  variant="compact"
  showSidebar={false}
  canvasWidth="var(--bloom-garden-canvas-width)"
  canvasHeight="var(--bloom-garden-canvas-height)"
>
  <main class="page-content">
    <GardenSelectionContent />
  </main>
</DesktopAppShell>

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
