<script lang="ts">
  import FilterButton from '../atoms/FilterButton.svelte';
  import PlanHistoryRow from '../molecules/PlanHistoryRow.svelte';
  import PaginationControls from '../molecules/PaginationControls.svelte';
  import type { PlanHistoryEntry, HistoryFilter } from '../../types';
  import { statisticsApi } from '../../api/statistics.api';

  let { startDate, endDate, itemsPerPage = 4 }: {
    startDate: Date;
    endDate: Date;
    itemsPerPage?: number;
  } = $props();

  let activeFilter = $state<HistoryFilter>('All');
  let currentPage = $state(1);

  let entries = $state<PlanHistoryEntry[]>([]);
  let totalItems = $state(0);
  let totalPages = $state(0);
  let loading = $state(false);
  let error = $state<string | null>(null);

  let currentFetchId = 0;
  let lastRangeKey = '';

  $effect(() => {
    if (!startDate || !endDate) return;
    const currentRangeKey = `${startDate.getTime()}-${endDate.getTime()}`;
    
    if (lastRangeKey !== '' && lastRangeKey !== currentRangeKey) {
      activeFilter = 'All';
      currentPage = 1;
    }
    lastRangeKey = currentRangeKey;

    fetchHistory(startDate, endDate, activeFilter, currentPage);
  });

  async function fetchHistory(sd: Date, ed: Date, filter: HistoryFilter, page: number) {
    if (!sd || !ed) return;
    const fetchId = ++currentFetchId;
    loading = true;
    error = null;
    try {
      const response = await statisticsApi.getPlanHistory(
        sd,
        ed,
        filter,
        page,
        itemsPerPage
      );
      if (fetchId !== currentFetchId) return;
      
      entries = response.items;
      totalItems = response.totalItems;
      totalPages = response.totalPages;
      
      if (page > totalPages && totalPages > 0) {
        currentPage = totalPages;
      }
    } catch (e: unknown) {
      if (fetchId !== currentFetchId) return;
      error = e instanceof Error ? e.message : 'Failed to load plan history';
      entries = [];
      totalItems = 0;
      totalPages = 0;
    } finally {
      if (fetchId === currentFetchId) {
        loading = false;
      }
    }
  }

  let showingCount = $derived(entries.length);

  function handleFilterChange(filter: HistoryFilter) {
    if (activeFilter !== filter) {
      activeFilter = filter;
      currentPage = 1;
    }
  }

  function handleNavigate(id: string) {
    // Navigate to plan details
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
        {#if loading}
          <tr>
            <td colspan="5" class="empty-state">Loading history...</td>
          </tr>
        {:else if error}
          <tr>
            <td colspan="5" class="empty-state error-text">
              {error}
              <br/>
              <button class="retry-btn" onclick={() => fetchHistory(startDate, endDate, activeFilter, currentPage)}>Retry</button>
            </td>
          </tr>
        {:else if entries.length > 0}
          {#each entries as entry (entry.id)}
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
    <PaginationControls 
      {currentPage} 
      totalPages={Math.max(1, totalPages)} 
      onPageChange={(page) => currentPage = page} 
    />
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

  .error-text {
    color: var(--bloom-text-red, #e74c3c);
  }

  .retry-btn {
    margin-top: 8px;
    padding: 4px 12px;
    border: 1px solid currentColor;
    background: transparent;
    border-radius: 4px;
    cursor: pointer;
    font-family: var(--bloom-body-font);
  }

  .retry-btn:hover {
    background: rgba(231, 76, 60, 0.1);
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
