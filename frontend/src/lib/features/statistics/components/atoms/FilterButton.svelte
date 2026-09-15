<script lang="ts">
  let { label, active, onClick }: {
    label: string;
    active: boolean;
    onClick: () => void;
  } = $props();
</script>

<button class="filter-button" class:active onclick={onClick}>
  {label}
</button>

<style>
  .filter-button {
    padding: 6px 16px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 16px;
    background: transparent;
    color: var(--bloom-text-muted-blue);
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .filter-button:hover {
    background: var(--bloom-surface-cream-alt);
  }

  .filter-button.active {
    background: var(--bloom-task-active-bg);
    border-color: var(--bloom-task-active-bg);
    color: var(--bloom-text-dark-blue);
    font-weight: 700;
  }

  .filter-button:focus-visible {
    outline: 2px solid var(--bloom-focus);
    outline-offset: 2px;
  }
</style>
