<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    id,
    labelId,
    label,
    description,
    descriptionId,
    children,
  }: {
    id?: string;
    labelId?: string;
    label: string;
    description?: string;
    descriptionId?: string;
    children?: Snippet;
  } = $props();
</script>

<div class="form-field">
  {#if id}
    <label class="field-label" for={id}>{label}</label>
  {:else}
    <div class="field-label" id={labelId}>{label}</div>
  {/if}
  <div class="field-control">
    {@render children?.()}
  </div>
  {#if description}
    <span class="field-description" id={descriptionId}>{description}</span>
  {/if}
</div>

<style>
  .form-field {
    display: grid;
    width: 100%;
    grid-template-columns: 210px minmax(0, 1fr);
    column-gap: 20px;
    align-items: start;
  }

  .field-label {
    margin-top: 8px;
    color: var(--bloom-text-dark-blue);
    font-family: var(--bloom-body-font);
    font-size: 18px;
    font-weight: 700;
    line-height: 1.25;
  }

  .field-control {
    display: flex;
    width: 100%;
    min-width: 0;
    flex-direction: column;
  }

  .field-description {
    grid-column: 2;
    margin-top: 4px;
    color: var(--bloom-text-muted-blue);
    font-family: var(--bloom-body-font);
    font-size: 16px;
    line-height: 1.3;
  }
</style>
