<script lang="ts">
  type BaseProps = {
    value?: string | number;
    placeholder?: string;
    type?: string;
    disabled?: boolean;
    onkeydown?: (e: KeyboardEvent) => void;
    variant?: "standard" | "composer";
  };

  type WithLabel = BaseProps & {
    id: string;
    label: string;
    error?: string;
  };

  type WithoutLabel = BaseProps & {
    id?: string;
    label?: never;
    error?: never;
  };

  let {
    id,
    label,
    value = $bindable(""),
    placeholder = "",
    error,
    type = "text",
    disabled = false,
    onkeydown,
    variant = "standard",
  }: WithLabel | WithoutLabel = $props();
</script>

{#if label}
  <div class="text-input-group">
    <label for={id}>{label}</label>
    <input
      {id}
      {type}
      bind:value
      {placeholder}
      {disabled}
      {onkeydown}
      class="text-input {variant}"
      class:has-error={!!error}
      aria-invalid={!!error}
      aria-describedby={error ? `${id}-error` : undefined}
    />
    {#if error}
      <span class="error-message" id={`${id}-error`} aria-live="polite"
        >{error}</span
      >
    {/if}
  </div>
{:else}
  <input
    {id}
    {type}
    bind:value
    {placeholder}
    {disabled}
    {onkeydown}
    class="text-input {variant}"
    class:has-error={!!error}
    aria-invalid={!!error}
  />
{/if}

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

  .text-input {
    font-family: var(--bloom-body-font);
    color: var(--bloom-text-dark-blue);
    box-sizing: border-box;
    width: 100%;
  }

  .text-input.standard {
    font-size: 16px;
    padding: 10px 14px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 4px;
    background: var(--bloom-surface-cream-alt);
  }

  .text-input.standard:focus-visible {
    outline: 2px solid var(--bloom-focus);
    outline-offset: 2px;
  }

  .text-input.composer {
    height: 72px;
    padding: 0 14px;
    border: 2px solid var(--bloom-chat-border);
    border-radius: 7px;
    font-size: 19px;
    background: var(--bloom-chat-surface);
  }

  .text-input.composer::placeholder {
    color: var(--bloom-text-muted-blue);
  }

  .text-input.composer:focus {
    outline: none;
    border-color: var(--bloom-chat-border-focus);
  }

  .text-input.composer:disabled {
    background: var(--bloom-chat-surface-disabled);
    opacity: 0.7;
    cursor: not-allowed;
  }

  .text-input.has-error {
    border-color: var(--bloom-error);
  }

  .error-message {
    grid-column: 2;
    color: var(--bloom-error);
    font-size: 13px;
    font-family: var(--bloom-body-font);
  }
</style>
