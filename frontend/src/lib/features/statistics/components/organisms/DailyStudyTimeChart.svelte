<script lang="ts">
  import BarChartColumn from '../atoms/BarChartColumn.svelte';
  import type { DailyStudyEntry } from '$lib/api/endpoints/statistics';

  let { entries, subtitle }: { entries: DailyStudyEntry[], subtitle: string } = $props();

  let maxHours = $derived(Math.max(1, ...entries.map(e => e.hours)));
</script>

<div class="daily-study-time-chart">
  <div class="chart-header">
    <h2>DAILY STUDY TIME</h2>
    <p class="subtitle">{subtitle}</p>
  </div>
  
  <div class="chart-area">
    {#each entries as entry}
      <BarChartColumn dayLabel={entry.dayLabel} hours={entry.hours} {maxHours} />
    {/each}
  </div>
</div>

<style>
  .daily-study-time-chart {
    background: var(--color-surface);
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 8px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    min-height: 260px;
    height: 100%;
  }

  .chart-header {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 24px;
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

  .subtitle {
    margin: 0;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    color: var(--bloom-text-muted-blue);
  }

  .chart-area {
    display: flex;
    justify-content: space-around;
    align-items: flex-end;
    flex: 1;
    padding-bottom: 8px;
  }
</style>
