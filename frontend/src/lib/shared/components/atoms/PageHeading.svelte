<script lang="ts">
  let { title, id, level = 'h1' }: {
    title: string;
    id?: string;
    level?: 'h1' | 'h2';
  } = $props();
</script>

<svelte:element this={level} {id} class="page-heading">{title}</svelte:element>

<style>
  .page-heading {
    margin: 0;
    color: var(--bloom-text-dark-blue);
    font-family: var(--bloom-display-font);
    font-size: 46px;
    font-weight: 900;
    letter-spacing: -0.06em;
    line-height: 1;
    text-shadow: 1px 0 currentColor;
    text-transform: uppercase;
  }
</style>
