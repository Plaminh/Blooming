<script lang="ts">
  let {
    id,
    value = $bindable(),
    options = [],
    required = false,
    disabled = false,
    ariaDescribedby,
  }: {
    id: string;
    value: string;
    options: Array<{ value: string; label: string }>;
    required?: boolean;
    disabled?: boolean;
    ariaDescribedby?: string;
  } = $props();

  function onChange(e: Event) {
    const target = e.target as HTMLSelectElement;
    value = target.value;
  }
</script>

<div class="select-wrapper">
  <select
    {id}
    {value}
    {required}
    {disabled}
    onchange={onChange}
    aria-describedby={ariaDescribedby} class="setup-select">
    {#each options as option}
      <option value={option.value}>{option.label}</option>
    {/each}
  </select>
  <div class="select-arrow">
    <svg width="12" height="8" viewBox="0 0 12 8" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M1.41 0.589966L6 5.16997L10.59 0.589966L12 1.99997L6 7.99997L0 1.99997L1.41 0.589966Z" fill="#214966"/>
    </svg>
  </div>
</div>

<style>
  .select-wrapper {
    position: relative;
    display: flex;
    width: 100%;
    height: 42px;
    align-items: center;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: var(--bloom-radius);
    background: var(--bloom-surface-cream-alt);
  }

  .select-wrapper:focus-within {
    outline: 2px solid #2d7c59;
    outline-offset: 2px;
  }

  .setup-select {
    width: 100%;
    height: 100%;
    padding: 0 42px 0 14px;
    border: none;
    outline: none;
    background: transparent;
    color: var(--bloom-text-control-blue);
    font-family: var(--bloom-body-font);
    font-size: 19px;
    appearance: none;
    -webkit-appearance: none;
    cursor: pointer;
  }

  .select-arrow {
    position: absolute;
    right: 15px;
    pointer-events: none;
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>
