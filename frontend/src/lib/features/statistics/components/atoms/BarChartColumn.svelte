<script lang="ts">
  let { dayLabel, hours, maxHours }: {
    dayLabel: string;
    hours: number;
    maxHours: number;
  } = $props();

  let percentage = $derived(maxHours > 0 ? (hours / maxHours) * 80 : 0);
  let isZero = $derived(hours === 0);
</script>

<div class="bar-chart-column" aria-label="{dayLabel}: {hours} hours">
  <div class="bar-container">
    {#if !isZero}
      <span class="value-label" style="bottom: {percentage}%">{hours}h</span>
      <div class="bar" style="height: {percentage}%"></div>
    {:else}
      <div class="zero-baseline"></div>
    {/if}
  </div>
  <span class="day-label">{dayLabel}</span>
</div>

<style>
  .bar-chart-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    height: 100%;
    width: 40px;
    gap: 12px;
  }

  .bar-container {
    position: relative;
    width: 100%;
    flex: 1;
    display: flex;
    align-items: flex-end;
    justify-content: center;
  }

  .bar {
    width: 100%;
    background-color: var(--bloom-primary-green);
    border-radius: 4px 4px 0 0;
  }

  .zero-baseline {
    width: 100%;
    height: 3px;
    background-color: var(--bloom-surface-dark-cream);
    border-radius: 2px;
  }

  .value-label {
    position: absolute;
    margin-bottom: 8px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 700;
    color: var(--bloom-text-dark-blue);
  }

  .day-label {
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 500;
    color: var(--bloom-text-muted-blue);
  }
</style>
