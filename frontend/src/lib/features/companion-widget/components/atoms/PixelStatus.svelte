<script lang="ts">
  import type { Snippet } from "svelte";

  type Props = {
    label: string;
    class?: string;
    children?: Snippet;
  };

  let { label, class: className = "", children }: Props = $props();
</script>

<span class="status {className}" role="img" aria-label={label}>
  {@render children?.()}
</span>

<style>
  .status {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;
  }
</style>
