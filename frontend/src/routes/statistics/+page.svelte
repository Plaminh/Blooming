<script lang="ts">
  import DesktopAppShell from '$lib/shared/components/organisms/DesktopAppShell.svelte';
  import StatisticsHeader from '$lib/features/statistics/components/organisms/StatisticsHeader.svelte';
  import SummaryCardRow from '$lib/features/statistics/components/organisms/SummaryCardRow.svelte';
  import StudyCalendarPanel from '$lib/features/statistics/components/organisms/StudyCalendarPanel.svelte';
  import DailyStudyTimeChart from '$lib/features/statistics/components/organisms/DailyStudyTimeChart.svelte';
  import PlanHistoryPanel from '$lib/features/statistics/components/organisms/PlanHistoryPanel.svelte';
  import { dateRanges, getStatisticsData } from '$lib/features/statistics/data/mockData';
  import type { StatisticsDateRange } from '$lib/features/statistics/types';

  let selectedRange = $state<StatisticsDateRange>(dateRanges[0]);
  let statsData = $derived(getStatisticsData(selectedRange.id));
</script>

<svelte:head>
  <title>Statistics - Blooming</title>
</svelte:head>

<DesktopAppShell activeRoute="STATISTICS" variant="compact">
  <main class="statistics-page" aria-label="Statistics content">
    <StatisticsHeader 
      ranges={dateRanges} 
      {selectedRange} 
      onRangeChange={(range) => selectedRange = range} 
    />
    <SummaryCardRow metrics={statsData.metrics} />

    <div class="two-column-layout">
      <div class="left-column">
        <StudyCalendarPanel studiedDays={statsData.calendarDays} />
      </div>
      <div class="right-column">
        <DailyStudyTimeChart 
          entries={statsData.dailyEntries} 
          subtitle={selectedRange.displayLabel} 
        />
      </div>
    </div>

    <PlanHistoryPanel entries={statsData.planEntries} itemsPerPage={4} />
  </main>
</DesktopAppShell>

<style>
  .statistics-page {
    padding: 20px 24px;
    height: 100%;
    overflow-y: auto;
    background-color: var(--bloom-surface-cream);
    color: var(--bloom-text-dark-blue);
    font-family: var(--bloom-body-font);
  }

  .two-column-layout {
    display: grid;
    grid-template-columns: 54% 1fr;
    gap: 16px;
    margin-bottom: 24px;
  }
</style>
