<script lang="ts">
  import type { Snippet } from "svelte";
  import type { HTMLButtonAttributes } from "svelte/elements";

  type Props = HTMLButtonAttributes & {
    variant?: "primary" | "ghost";
    children?: Snippet;
  };

  let {
    variant = "primary",
    type = "button",
    class: className = "",
    children,
    ...rest
  }: Props = $props();
</script>

<button class="button {variant} {className}" {type} {...rest}>
  {@render children?.()}
</button>

<style>
  .button {
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    padding: var(--space-2) var(--space-4);
    cursor: pointer;
  }

  .button:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }

  .primary {
    background: var(--color-accent);
    border-color: var(--color-accent);
    color: #ffffff;
  }

  .ghost {
    background: transparent;
    color: var(--color-text);
  }
</style>
