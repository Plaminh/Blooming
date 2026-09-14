<script lang="ts" generics="T">
  let {
    id,
    label,
    value = $bindable(),
    options,
    error
  }: {
    id: string;
    label: string;
    value: T;
    options: { value: T; label: string }[];
    error?: string;
  } = $props();
</script>

<div class="select-group">
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
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 20px;
  }

  label {
    font-family: var(--bloom-body-font);
    font-size: 16px;
    color: var(--bloom-text-dark-blue);
    font-weight: 600;
  }

  select {
    font-family: var(--bloom-body-font);
    font-size: 16px;
    color: var(--bloom-text-dark-blue);
    padding: 10px 14px;
    border: 1px solid #cfc9b9;
    border-radius: 4px;
    background: #ffffff;
    cursor: pointer;
  }

  select:focus-visible {
    outline: 2px solid var(--bloom-text-control-blue);
    outline-offset: 2px;
  }

  select.has-error {
    border-color: #d32f2f;
  }

  .error-message {
    color: #d32f2f;
    font-size: 13px;
    font-family: var(--bloom-body-font);
  }
</style>
