<script lang="ts">
  import PageHeading from '$lib/shared/components/atoms/PageHeading.svelte';
  import DateRangeSelector from '../molecules/DateRangeSelector.svelte';
  import type { StatisticsDateRange } from '../../types';

  let { ranges, selectedRange, onRangeChange }: {
    ranges: StatisticsDateRange[];
    selectedRange: StatisticsDateRange;
    onRangeChange: (range: StatisticsDateRange) => void;
  } = $props();
</script>

<header class="statistics-header">
  <div class="title-container">
    <PageHeading title="STATISTICS" />
    <p class="page-subtitle">Your progress, one day at a time.</p>
  </div>
  <div class="selector-container">
    <DateRangeSelector {ranges} {selectedRange} onSelect={onRangeChange} />
  </div>
</header>

<style>
  .statistics-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
  }

  .title-container {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .page-subtitle {
    margin: 0;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    color: var(--bloom-text-muted-blue);
  }

  .selector-container {
    display: flex;
    align-items: center;
  }
</style>
