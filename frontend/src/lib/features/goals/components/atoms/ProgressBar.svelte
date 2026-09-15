<script lang="ts">
  let { percentage, label }: { percentage: string; label?: string } = $props();
</script>

<div class="progress-container">
  <div class="progress-bar-wrap">
    <div class="progress-fill" style="width: {percentage}"></div>
  </div>
  {#if label}
    <span class="progress-label">{label}</span>
  {/if}
</div>

<style>
  .progress-container {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .progress-bar-wrap {
    flex: 1;
    height: 26px;
    background: #e7e2d5;
    border-radius: 5px;
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    background: #50a469;
    border-radius: 5px;
  }
  .progress-label {
    font-family: var(--bloom-body-font);
    font-size: 24px;
    font-weight: 700;
    color: #064b91;
  }
</style>
