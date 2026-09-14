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

  input {
    font-family: var(--bloom-body-font);
    font-size: 16px;
    color: var(--bloom-text-dark-blue);
    padding: 10px 14px;
    border: 1px solid #cfc9b9;
    border-radius: 4px;
    background: #ffffff;
  }

  input:focus-visible {
    outline: 2px solid var(--bloom-text-control-blue);
    outline-offset: 2px;
  }

  input.has-error {
    border-color: #d32f2f;
  }

  .error-message {
    color: #d32f2f;
    font-size: 13px;
    font-family: var(--bloom-body-font);
  }
</style>
