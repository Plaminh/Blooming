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
    color: #1e3a5f;
    margin: 24px 0;
  }
  h2 {
    font-family: var(--bloom-display-font);
    font-size: 32px;
    margin: 0 0 12px 0;
    text-transform: uppercase;
  }
  p {
    font-family: var(--bloom-body-font);
    font-size: 16px;
    margin: 4px 0;
  }
</style>
