<script lang="ts">
  let {
    id,
    value = $bindable(),
    placeholder = '',
    required = false,
    maxlength,
    disabled = false,
    ariaDescribedby,
  }: {
    id: string;
    value: string;
    placeholder?: string;
    required?: boolean;
    maxlength?: number;
    disabled?: boolean;
    ariaDescribedby?: string;
  } = $props();
</script>

<div class="input-wrapper">
  <input
    {id}
    type="text"
    bind:value
    {placeholder}
    {required}
    {maxlength}
    {disabled}
    aria-describedby={ariaDescribedby}
    class="setup-input"
  />
</div>

<style>
  .input-wrapper {
    display: flex;
    width: 100%;
    height: 42px;
    align-items: center;
    padding: 0 14px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: var(--bloom-radius);
    background: var(--bloom-surface-cream-alt);
    transition: border-color 0.2s;
  }

  .input-wrapper:focus-within {
    outline: 2px solid #2d7c59;
    outline-offset: 2px;
  }

  .setup-input {
    width: 100%;
    height: 100%;
    border: none;
    outline: none;
    background: transparent;
    min-width: 0;
    color: var(--bloom-text-control-blue);
    font-family: var(--bloom-body-font);
    font-size: 19px;
  }

  .setup-input::placeholder {
    color: #8ba0aa;
  }
</style>
