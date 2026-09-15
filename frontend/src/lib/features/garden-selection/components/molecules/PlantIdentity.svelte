<script lang="ts">
  let { name, description }: { name: string; description: string[] } = $props();
</script>

<div class="plant-identity" aria-live="polite">
  <h2>{name}</h2>
  {#each description as line}
    <p>{line}</p>
  {/each}
</div>

<style>
  .plant-identity {
    text-align: center;
    color: var(--bloom-text-dark-blue);
    margin: 4px 0 8px;
  }
  h2 {
    font-family: var(--bloom-display-font);
    font-size: 24px;
    margin: 0 0 2px;
  }
  p {
    font-family: var(--bloom-body-font);
    font-size: 16px;
    margin: 0;
  }
</style>
