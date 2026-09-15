<script lang="ts">
  let {
    id,
    label,
    value = $bindable(),
    error,
    type = "text"
  }: {
    id: string;
    label: string;
    value: string;
    error?: string;
    type?: string;
  } = $props();
</script>

<div class="text-input-group">
  <label for={id}>{label}</label>
  <input
    {id}
    {type}
    bind:value
    class:has-error={!!error}
    aria-invalid={!!error}
    aria-describedby={error ? `${id}-error` : undefined}
  />
  {#if error}
    <span class="error-message" id={`${id}-error`} aria-live="polite">{error}</span>
  {/if}
</div>

<style>
  .text-input-group {
    display: grid;
    grid-template-columns: 220px minmax(0, 1fr);
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
  }

  label {
    font-family: var(--bloom-body-font);
    font-size: 16px;
    color: var(--bloom-text-dark-blue);
    font-weight: 600;
  }

  input {
    font-family: var(--bloom-body-font);
    font-size: 16px;
    color: var(--bloom-text-dark-blue);
    padding: 10px 14px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 4px;
    background: var(--bloom-surface-cream-alt);
  }

  input:focus-visible {
    outline: 2px solid var(--bloom-focus);
    outline-offset: 2px;
  }

  input.has-error {
    border-color: var(--bloom-error);
  }

  .error-message {
    grid-column: 2;
    color: var(--bloom-error);
    font-size: 13px;
    font-family: var(--bloom-body-font);
  }
</style>
