<script lang="ts">
  import SummaryCard from '../atoms/SummaryCard.svelte';
  import type { SummaryMetrics } from '../../types';

  let { metrics }: { metrics: SummaryMetrics } = $props();
</script>

<div class="summary-card-row">
  <SummaryCard iconName="clock" label="STUDY TIME">
    {#snippet value()}
      {metrics.studyTimeHours}h {metrics.studyTimeMinutes}m
    {/snippet}
  </SummaryCard>
  
  <SummaryCard iconName="calendar" label="STUDY DAYS">
    {#snippet value()}
      {metrics.studyDayCount} days
    {/snippet}
  </SummaryCard>

  <SummaryCard iconName="document" label="PLANS">
    {#snippet value()}
      {metrics.completedPlanCount} complete <span class="muted">/ {metrics.unfinishedPlanCount} unfinished</span>
    {/snippet}
  </SummaryCard>
</div>

<style>
  .summary-card-row {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
  }

  .muted {
    font-size: 16px;
    color: var(--bloom-text-muted-blue);
    font-weight: 500;
  }
</style>
