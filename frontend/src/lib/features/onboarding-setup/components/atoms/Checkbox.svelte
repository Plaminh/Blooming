<script lang="ts">
  let {
    id,
    checked = $bindable(),
    label,
    description
  }: {
    id: string;
    checked: boolean;
    label: string;
    description?: string;
  } = $props();
</script>

<div class="checkbox-container">
  <label class="checkbox-label" for={id}>
    <span class="checkbox-wrapper">
      <input
        type="checkbox"
        {id}
        bind:checked
        aria-describedby={description ? `${id}-description` : undefined}
        class="sr-only"
      />
      <span class="custom-checkbox" class:checked>
        {#if checked}
          <svg width="16" height="12" viewBox="0 0 16 12" fill="none" aria-hidden="true">
            <path d="m1.5 6 4 4 9-8.5" stroke="white" stroke-width="2.5" fill="none" />
          </svg>
        {/if}
      </span>
    </span>
    <span class="label-text">{label}</span>
  </label>
  {#if description}
    <span id={`${id}-description`} class="description-text">{description}</span>
  {/if}
</div>

<style>
  .checkbox-container {
    display: grid;
    grid-template-columns: 30px minmax(0, 1fr);
    column-gap: 14px;
    row-gap: 1px;
    cursor: pointer;
  }

  .checkbox-label {
    display: contents;
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  }

  .checkbox-wrapper {
    position: relative;
    display: flex;
    grid-row: 1 / span 2;
    grid-column: 1;
    align-items: center;
    justify-content: center;
    padding-top: 0;
  }

  .custom-checkbox {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border: 2px solid var(--bloom-primary-green-border);
    border-radius: var(--bloom-radius);
    background: var(--bloom-surface-cream-alt);
    transition: all 0.2s;
  }

  .custom-checkbox.checked {
    background: var(--bloom-primary-green);
    border-color: var(--bloom-primary-green-border);
  }

  input:focus-visible + .custom-checkbox {
    outline: 2px solid #2d7c59;
    outline-offset: 2px;
  }

  .label-text {
    grid-row: 1;
    grid-column: 2;
    color: var(--bloom-text-control-blue);
    font-size: 18px;
    font-weight: 700;
    cursor: pointer;
  }

  .description-text {
    grid-row: 2;
    grid-column: 2;
    color: var(--bloom-text-muted-blue);
    font-size: 15px;
    line-height: 1.35;
  }
</style>
