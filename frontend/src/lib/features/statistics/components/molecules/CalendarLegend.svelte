<div class="calendar-legend">
  <div class="legend-item">
    <span class="swatch studied"></span>
    <span class="label">Studied</span>
  </div>
  <div class="legend-item">
    <span class="swatch no-record"></span>
    <span class="label">No record</span>
  </div>
</div>

<style>
  .calendar-legend {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .swatch {
    width: 12px;
    height: 12px;
    border-radius: 2px;
  }

  .swatch.studied {
    background-color: var(--bloom-task-completed-bg);
  }

  .swatch.no-record {
    background-color: var(--bloom-surface-dark-cream);
  }

  .label {
    font-family: var(--bloom-body-font);
    font-size: 12px;
    color: var(--bloom-text-muted-blue);
  }
</style>
