<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { monthLabel, onPrev, onNext }: {
    monthLabel: string;
    onPrev: () => void;
    onNext: () => void;
  } = $props();
</script>

<div class="calendar-month-nav">
  <button class="nav-button" onclick={onPrev} aria-label="Previous month">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>
  <span class="month-label">{monthLabel}</span>
  <button class="nav-button" onclick={onNext} aria-label="Next month">
    <AppIcon name="chevron-right" size="task-type" />
  </button>
</div>

<style>
  .calendar-month-nav {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .nav-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 4px;
    background: var(--bloom-action-secondary-bg);
    color: var(--bloom-text-dark-blue);
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .nav-button:hover {
    background: var(--bloom-surface-cream-alt);
  }
  
  .nav-button:focus-visible {
    outline: 2px solid var(--bloom-focus);
    outline-offset: 2px;
  }

  .month-label {
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 700;
    color: var(--bloom-text-dark-blue);
    min-width: 100px;
    text-align: center;
  }
</style>
