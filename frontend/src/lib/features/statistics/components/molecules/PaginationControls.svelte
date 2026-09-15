<script lang="ts">
  let { currentPage, totalPages, onPageChange }: {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
  } = $props();

  let prevDisabled = $derived(currentPage <= 1);
  let nextDisabled = $derived(currentPage >= totalPages || totalPages === 0);
</script>

<div class="pagination-controls">
  <button 
    class="page-btn" 
    disabled={prevDisabled} 
    aria-label="Previous page"
    onclick={() => onPageChange(currentPage - 1)}
  >
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>
  
  <span class="page-indicator">{totalPages > 0 ? currentPage : 0} / {totalPages}</span>
  
  <button 
    class="page-btn" 
    disabled={nextDisabled} 
    aria-label="Next page"
    onclick={() => onPageChange(currentPage + 1)}
  >
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>
</div>

<style>
  .pagination-controls {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .page-btn {
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
  }

  .page-btn:hover:not(:disabled) {
    background: var(--bloom-surface-cream-alt);
  }

  .page-btn:disabled {
    color: var(--bloom-disabled);
    cursor: not-allowed;
    border-color: var(--bloom-border-subtle);
  }
  
  .page-btn:focus-visible {
    outline: 2px solid var(--bloom-focus);
  }

  .page-indicator {
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 500;
    color: var(--bloom-text-dark-blue);
    min-width: 40px;
    text-align: center;
  }
</style>
