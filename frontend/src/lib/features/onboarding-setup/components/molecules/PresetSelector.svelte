<script lang="ts">
  import type { FocusPreset } from '../../model/OnboardingSetupState.svelte';

  let {
    selected = $bindable(),
    labelledby,
    describedby,
    options = [
      { value: '25 / 5', label: '25 / 5' },
      { value: '50 / 10', label: '50 / 10' },
      { value: 'CUSTOM', label: 'CUSTOM' },
    ],
  }: {
    selected: FocusPreset;
    labelledby?: string;
    describedby?: string;
    options?: { value: FocusPreset; label: string }[];
  } = $props();
</script>

<div
  class="preset-buttons"
  role="group"
  aria-labelledby={labelledby}
  aria-describedby={describedby}
>
  {#each options as option}
    <button
      type="button"
      class="preset-button"
      class:active={selected === option.value}
      aria-pressed={selected === option.value}
      onclick={() => (selected = option.value)}
    >
      {option.label}
    </button>
  {/each}
</div>

<style>
  .preset-buttons {
    display: grid;
    width: 100%;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }

  .preset-button {
    height: 54px;
    margin: 0;
    padding: 0;
    border: 1px solid var(--bloom-border-dark);
    border-radius: var(--bloom-radius);
    background: var(--bloom-surface-dark-cream);
    color: var(--bloom-text-control-blue);
    cursor: pointer;
    font-family: var(--bloom-body-font);
    font-size: 20px;
    font-weight: 700;
    line-height: 1;
  }

  .preset-button.active {
    border: 2px solid var(--bloom-primary-green-border);
    background: var(--bloom-primary-green);
    color: #f1f6ec;
  }

  .preset-button:focus-visible {
    outline: 2px solid #2d7c59;
    outline-offset: 2px;
  }
</style>
