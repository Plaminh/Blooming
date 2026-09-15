<script lang="ts">
  import PlanningWorkspace from '$lib/features/mr-bloom/components/organisms/PlanningWorkspace.svelte';
  import DesktopAppShell from '$lib/shared/components/organisms/DesktopAppShell.svelte';
</script>

<svelte:head>
  <title>Mr. Bloom - Blooming</title>
</svelte:head>

<DesktopAppShell activeRoute="MR. BLOOM">
  <PlanningWorkspace />
</DesktopAppShell>
