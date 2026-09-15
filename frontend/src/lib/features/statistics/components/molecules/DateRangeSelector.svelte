<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import type { StatisticsDateRange } from '../../types';

  let { ranges, selectedRange, onSelect }: {
    ranges: StatisticsDateRange[];
    selectedRange: StatisticsDateRange;
    onSelect: (range: StatisticsDateRange) => void;
  } = $props();

  let isOpen = $state(false);

  function toggleOpen() {
    isOpen = !isOpen;
  }

  function handleSelect(range: StatisticsDateRange) {
    onSelect(range);
    isOpen = false;
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      isOpen = false;
    }
  }

  function handleOutsideClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest('.date-range-container')) {
      isOpen = false;
    }
  }
</script>

<svelte:window on:click={handleOutsideClick} on:keydown={handleKeydown} />

<div class="date-range-container">
  <button 
    class="date-range-toggle" 
    onclick={toggleOpen}
    aria-expanded={isOpen}
    aria-haspopup="listbox"
  >
    <AppIcon name="calendar" size="task-type" />
    <span class="label">{selectedRange.displayLabel}</span>
    <span class="chevron" class:open={isOpen}>
      <AppIcon name="chevron-right" size="task-type" />
    </span>
  </button>

  {#if isOpen}
    <ul class="date-range-dropdown" role="listbox">
      {#each ranges as range}
        <li role="option" aria-selected={range.id === selectedRange.id}>
          <button 
            class="dropdown-item" 
            class:selected={range.id === selectedRange.id}
            onclick={() => handleSelect(range)}
          >
            {range.displayLabel}
          </button>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .date-range-container {
    position: relative;
    display: inline-block;
  }

  .date-range-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: var(--bloom-action-secondary-bg);
    border: 1px solid var(--bloom-border-subtle);
    border-radius: var(--bloom-radius);
    color: var(--bloom-text-dark-blue);
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s;
  }

  .date-range-toggle:hover {
    background: var(--bloom-surface-cream-alt);
  }

  .date-range-toggle:focus-visible {
    outline: 2px solid var(--bloom-focus);
    outline-offset: -2px;
  }

  .chevron {
    display: flex;
    align-items: center;
    transition: transform 0.2s;
  }

  .chevron.open {
    transform: rotate(90deg);
  }

  .date-range-dropdown {
    position: absolute;
    top: calc(100% + 4px);
    right: 0;
    z-index: 10;
    min-width: 200px;
    margin: 0;
    padding: 8px 0;
    list-style: none;
    background: var(--color-surface);
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .dropdown-item {
    display: block;
    width: 100%;
    padding: 8px 16px;
    border: none;
    background: transparent;
    color: var(--bloom-text-dark-blue);
    font-family: var(--bloom-body-font);
    font-size: 14px;
    text-align: left;
    cursor: pointer;
  }

  .dropdown-item:hover, .dropdown-item:focus-visible {
    background: var(--bloom-surface-cream-alt);
    outline: none;
  }

  .dropdown-item.selected {
    font-weight: 700;
    background: var(--bloom-task-completed-bg);
  }
</style>
