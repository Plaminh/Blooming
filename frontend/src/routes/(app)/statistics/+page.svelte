<script lang="ts">
  import StatisticsHeader from '$lib/features/statistics/components/organisms/StatisticsHeader.svelte';
  import SummaryCardRow from '$lib/features/statistics/components/organisms/SummaryCardRow.svelte';
  import StudyCalendarPanel from '$lib/features/statistics/components/organisms/StudyCalendarPanel.svelte';
  import DailyStudyTimeChart from '$lib/features/statistics/components/organisms/DailyStudyTimeChart.svelte';
  import PlanHistoryPanel from '$lib/features/statistics/components/organisms/PlanHistoryPanel.svelte';
  import type { StatisticsDateRange, SummaryMetrics, DailyStudyEntry } from '$lib/features/statistics/types';
  import { statisticsApi } from '$lib/features/statistics/api/statistics.api';

  export const dateRanges: StatisticsDateRange[] = [
    {
      id: 'current-week',
      startDate: (() => {
        const d = new Date();
        d.setDate(d.getDate() - d.getDay() + (d.getDay() === 0 ? -6 : 1)); // Monday
        return d;
      })(),
      endDate: (() => {
        const d = new Date();
        d.setDate(d.getDate() - d.getDay() + (d.getDay() === 0 ? -6 : 1) + 6); // Sunday
        return d;
      })(),
      displayLabel: 'Current Week'
    },
    {
      id: 'last-week',
      startDate: (() => {
        const d = new Date();
        d.setDate(d.getDate() - d.getDay() + (d.getDay() === 0 ? -6 : 1) - 7);
        return d;
      })(),
      endDate: (() => {
        const d = new Date();
        d.setDate(d.getDate() - d.getDay() + (d.getDay() === 0 ? -6 : 1) - 1);
        return d;
      })(),
      displayLabel: 'Last Week'
    },
    {
      id: 'current-month',
      startDate: (() => {
        const d = new Date();
        return new Date(d.getFullYear(), d.getMonth(), 1);
      })(),
      endDate: (() => {
        const d = new Date();
        return new Date(d.getFullYear(), d.getMonth() + 1, 0);
      })(),
      displayLabel: 'Current Month'
    }
  ];

  let selectedRange = $state<StatisticsDateRange>(dateRanges[0]);

  let metrics = $state<SummaryMetrics>({
    studyTimeHours: 0,
    studyTimeMinutes: 0,
    studyDayCount: 0,
    completedPlanCount: 0,
    unfinishedPlanCount: 0
  });

  let dailyEntries = $state<DailyStudyEntry[]>([]);
  let calendarDays = $derived(
    dailyEntries
      .filter(e => e.hours > 0)
      .map(e => ({
        day: parseInt(e.date.split('-')[2], 10),
        status: 'studied' as const
      }))
  );

  let error = $state<string | null>(null);
  let currentFetchId = 0;

  $effect(() => {
    async function fetchData() {
      if (!selectedRange) return;
      const fetchId = ++currentFetchId;
      error = null;
      try {
        const [summary, daily] = await Promise.all([
          statisticsApi.getSummary(selectedRange.startDate, selectedRange.endDate),
          statisticsApi.getDaily(selectedRange.startDate, selectedRange.endDate)
        ]);
        if (fetchId !== currentFetchId) return;
        metrics = summary;
        dailyEntries = daily;
      } catch (e: unknown) {
        if (fetchId !== currentFetchId) return;
        error = e instanceof Error ? e.message : 'Failed to load statistics';
        metrics = {
          studyTimeHours: 0,
          studyTimeMinutes: 0,
          studyDayCount: 0,
          completedPlanCount: 0,
          unfinishedPlanCount: 0
        };
        dailyEntries = [];
      }
    }
    fetchData();
  });
</script>

<svelte:head>
  <title>Statistics - Blooming</title>
</svelte:head>

<main class="statistics-page" aria-label="Statistics content">
  <StatisticsHeader 
    ranges={dateRanges} 
    {selectedRange} 
    onRangeChange={(range) => selectedRange = range} 
  />
  
  {#if error}
    <div class="error-banner">
      {error}
      <button class="retry-btn" onclick={() => selectedRange = {...selectedRange}}>Retry</button>
    </div>
  {/if}

  <SummaryCardRow {metrics} />

  <div class="two-column-layout">
    <div class="left-column">
      <StudyCalendarPanel studiedDays={calendarDays} />
    </div>
    <div class="right-column">
      <DailyStudyTimeChart 
        entries={dailyEntries} 
        subtitle={selectedRange.displayLabel} 
      />
    </div>
  </div>

  <PlanHistoryPanel startDate={selectedRange.startDate} endDate={selectedRange.endDate} itemsPerPage={4} />
</main>

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

  .error-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: rgba(231, 76, 60, 0.1);
    color: var(--bloom-text-red, #e74c3c);
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    border: 1px solid rgba(231, 76, 60, 0.3);
  }

  .retry-btn {
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
</style>
