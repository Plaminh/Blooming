<script lang="ts">
  let { children } = $props();
</script>

<div class="root">
  {@render children()}
</div>

<style>
  :global(html),
  :global(body) {
    margin: 0;
    overflow: hidden;
    width: 100%;
    height: 100%;
    background: #0e3052;
  }

  .root {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }

  .root :global(.companion-widget) {
    transform-origin: top left;
    transform: scale(min(100vw / 680px, 100vh / 289px));
  }
</style>
