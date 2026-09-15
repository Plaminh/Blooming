<script lang="ts">
  import FilterButton from '../atoms/FilterButton.svelte';
  import PlanHistoryRow from '../molecules/PlanHistoryRow.svelte';
  import PaginationControls from '../molecules/PaginationControls.svelte';
  import type { PlanHistoryEntry, HistoryFilter } from '../../types';

  let { entries = [], itemsPerPage = 4 }: {
    entries: PlanHistoryEntry[];
    itemsPerPage?: number;
  } = $props();

  let activeFilter = $state<HistoryFilter>('All');
  let currentPage = $state(1);

  // When entries change (e.g. from date range change), reset filter and page
  $effect(() => {
    if (entries) {
      activeFilter = 'All';
      currentPage = 1;
    }
  });

  let filteredEntries = $derived(
    activeFilter === 'All' 
      ? entries 
      : entries.filter(e => e.status === activeFilter)
  );

  let totalItems = $derived(filteredEntries.length);
  let totalPages = $derived(Math.ceil(totalItems / itemsPerPage));
  let visibleEntries = $derived(
    filteredEntries.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
  );
  let showingCount = $derived(visibleEntries.length);

  function handleFilterChange(filter: HistoryFilter) {
    activeFilter = filter;
    currentPage = 1; // Reset to first page when filtering
  }

  function handleNavigate(id: string) {
    console.log('Navigate to plan details', id);
  }
</script>

<div class="plan-history-panel">
  <div class="panel-header">
    <h2>PLAN HISTORY</h2>
    <div class="filter-controls">
      <FilterButton label="All" active={activeFilter === 'All'} onClick={() => handleFilterChange('All')} />
      <FilterButton label="Completed" active={activeFilter === 'Completed'} onClick={() => handleFilterChange('Completed')} />
      <FilterButton label="Unfinished" active={activeFilter === 'Unfinished'} onClick={() => handleFilterChange('Unfinished')} />
    </div>
  </div>

  <div class="table-container">
    <table>
      <thead>
        <tr>
          <th class="date-col">DATE</th>
          <th class="name-col">PLAN</th>
          <th class="tasks-col">TASKS</th>
          <th class="status-col">STATUS</th>
          <th class="action-col"></th>
        </tr>
      </thead>
      <tbody>
        {#if visibleEntries.length > 0}
          {#each visibleEntries as entry (entry.id)}
            <PlanHistoryRow {entry} onNavigate={handleNavigate} />
          {/each}
        {:else}
          <tr>
            <td colspan="5" class="empty-state">No plans found</td>
          </tr>
        {/if}
      </tbody>
    </table>
  </div>

  <div class="panel-footer">
    <span class="showing-text">Showing {showingCount} of {totalItems} plans</span>
    <PaginationControls {currentPage} {totalPages} onPageChange={(page) => currentPage = page} />
  </div>
</div>

<style>
  .plan-history-panel {
    background: var(--color-surface);
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 8px;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  h2 {
    margin: 0;
    font-family: var(--bloom-display-font);
    font-size: var(--bloom-panel-title-size);
    font-weight: var(--bloom-panel-title-weight);
    letter-spacing: var(--bloom-panel-title-tracking);
    line-height: var(--bloom-panel-title-line-height);
    color: var(--bloom-text-dark-blue);
  }

  .filter-controls {
    display: flex;
    gap: 8px;
  }

  .table-container {
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
  }

  th {
    padding: 0 8px 12px;
    font-family: var(--bloom-body-font);
    font-size: 12px;
    font-weight: 700;
    color: var(--bloom-text-muted-blue);
    border-bottom: 1px solid var(--bloom-border-subtle);
  }

  .date-col { width: 15%; }
  .name-col { width: 45%; }
  .tasks-col { width: 15%; }
  .status-col { width: 20%; }
  .action-col { width: 5%; }

  .empty-state {
    text-align: center;
    padding: 32px;
    color: var(--bloom-text-muted-blue);
    font-style: italic;
  }

  .panel-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 4px;
  }

  .showing-text {
    font-family: var(--bloom-body-font);
    font-size: 14px;
    color: var(--bloom-text-muted-blue);
  }
</style>
