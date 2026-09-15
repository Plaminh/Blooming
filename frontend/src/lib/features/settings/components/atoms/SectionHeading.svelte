<script lang="ts">
  import PageHeading from '$lib/shared/components/atoms/PageHeading.svelte';

  let { title }: { title: string } = $props();
</script>

<div class="section-heading">
  <PageHeading {title} level="h2" />
</div>

<style>
  .section-heading {
    margin-bottom: 24px;
  }
</style>
