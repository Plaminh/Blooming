<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    type = 'button',
    variant = 'primary',
    disabled = false,
    onclick,
    children
  }: {
    type?: 'button' | 'submit' | 'reset';
    variant?: 'primary' | 'secondary';
    disabled?: boolean;
    onclick?: (e: MouseEvent) => void;
    children?: Snippet;
  } = $props();
</script>

<button
  {type}
  {disabled}
  class="btn btn-{variant}"
  {onclick}
>
  {@render children?.()}
</button>

<style>
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: 60px;
    padding: 0 28px;
    border-radius: var(--bloom-radius);
    font-family: var(--bloom-display-font);
    font-size: 21px;
    font-weight: 800;
    letter-spacing: 0.04em;
    cursor: pointer;
    border: 1px solid transparent;
    transition: background-color 0.2s;
  }

  .btn:focus-visible {
    outline: 2px solid #225f48;
    outline-offset: 2px;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-primary {
    background: var(--bloom-primary-green);
    border-color: var(--bloom-primary-green-border);
    color: #eef5e9;
  }

  .btn-primary:hover:not(:disabled) {
    background: var(--bloom-primary-green-hover);
  }

  .btn-secondary {
    background: var(--bloom-surface-dark-cream);
    border-color: var(--bloom-border-dark);
    color: var(--bloom-text-control-blue);
  }

  .btn-secondary:hover:not(:disabled) {
    background: #ebdcc0;
  }
</style>
