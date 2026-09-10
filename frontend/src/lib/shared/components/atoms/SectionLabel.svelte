<script lang="ts">
  import type { Snippet } from "svelte";

  type Props = {
    children: Snippet;
  };

  let { children }: Props = $props();
</script>

<span class="section-label">{@render children()}</span>

<style>
  .section-label {
    color: var(--color-muted);
    font-size: 0.875rem;
    letter-spacing: 0.02em;
  }
</style>
