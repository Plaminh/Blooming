<script lang="ts">
  let {
    hour,
    kind = 'small'
  }: {
    hour: string;
    kind?: 'active' | 'completed' | 'upcoming' | 'small';
  } = $props();
</script>

<div class="time-marker {kind}">
  <span class="time-label">{hour}</span>
  <span class="marker-dot" aria-hidden="true">
    {#if kind === 'completed'}<span class="check"></span>{/if}
  </span>
</div>

<style>
  .time-marker {
    position: absolute;
    left: 0;
    display: flex;
    width: var(--timeline-hour-column-width, 112px);
    height: 24px;
    align-items: center;
  }

  .time-label {
    width: var(--timeline-hour-label-width, 72px);
    color: #0753a6;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    font-weight: 500;
    text-align: left;
    white-space: nowrap;
  }

  .marker-dot {
    position: absolute;
    left: var(--timeline-marker-offset, 85px);
    width: 12px;
    height: 12px;
    border: 0;
    border-radius: 50%;
    background: #aeb8c1;
  }

  .active .marker-dot,
  .upcoming .marker-dot,
  .completed .marker-dot {
    width: 26px;
    height: 26px;
    border: 5px solid #24abe7;
    background: #fffdf5;
    transform: translateX(-7px);
  }

  .upcoming .marker-dot { border-color: #aeb8c1; }
  .completed .marker-dot {
    border: 0;
    background: #319460;
  }

  .check {
    position: absolute;
    top: 7px;
    left: 6px;
    width: 13px;
    height: 7px;
    border-bottom: 2px solid white;
    border-left: 2px solid white;
    transform: rotate(-45deg);
  }
</style>
