<script lang="ts">
  let { children }: { children: import('svelte').Snippet } = $props();
</script>

<h2 class="panel-heading">{@render children()}</h2>

<style>
  .panel-heading {
    color: #071f66;
    font-family: var(--bloom-display-font);
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.055em;
    line-height: 1.15;
  }
</style>
