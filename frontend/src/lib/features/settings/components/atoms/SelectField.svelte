<script lang="ts" generics="T">
  let {
    id,
    label,
    value = $bindable(),
    options,
    error,
    layout = 'inline',
  }: {
    id: string;
    label: string;
    value: T;
    options: { value: T; label: string }[];
    error?: string;
    layout?: 'inline' | 'stacked';
  } = $props();
</script>

<div class="select-group" class:stacked={layout === 'stacked'}>
  <label for={id}>{label}</label>
  <select
    {id}
    bind:value
    class:has-error={!!error}
    aria-invalid={!!error}
    aria-describedby={error ? `${id}-error` : undefined}
  >
    {#each options as option}
      <option value={option.value}>{option.label}</option>
    {/each}
  </select>
  {#if error}
    <span class="error-message" id={`${id}-error`} aria-live="polite">{error}</span>
  {/if}
</div>

<style>
  .select-group {
    display: grid;
    grid-template-columns: 220px minmax(0, 1fr);
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
  }

  .select-group.stacked {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    margin-bottom: 0;
  }

  label {
    font-family: var(--bloom-body-font);
    font-size: 16px;
    color: var(--bloom-text-dark-blue);
    font-weight: 600;
  }

  select {
    box-sizing: border-box;
    width: 100%;
    min-height: 44px;
    font-family: var(--bloom-body-font);
    font-size: 16px;
    color: var(--bloom-text-dark-blue);
    padding: 10px 14px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 4px;
    background: var(--bloom-surface-cream-alt);
    cursor: pointer;
    transition: border-color 0.15s ease, background-color 0.15s ease;
  }

  select:hover {
    border-color: var(--bloom-border-dark);
  }

  select:focus-visible {
    outline: 2px solid var(--bloom-focus);
    outline-offset: 2px;
  }

  select.has-error {
    border-color: var(--bloom-error);
  }

  .error-message {
    grid-column: 2;
    color: var(--bloom-error);
    font-size: 13px;
    font-family: var(--bloom-body-font);
  }

  .stacked .error-message {
    grid-column: auto;
  }
</style>
