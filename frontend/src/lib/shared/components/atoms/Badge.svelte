<script lang="ts">
  import type { Snippet } from "svelte";

  type Props = {
    children: Snippet;
  };

  let { children }: Props = $props();
</script>

<span class="badge">{@render children()}</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    border: 1px solid var(--color-border);
    border-radius: 999px;
    padding: 0.1rem 0.55rem;
    background: var(--color-surface);
    color: var(--color-muted);
    font-size: 0.75rem;
  }
</style>
