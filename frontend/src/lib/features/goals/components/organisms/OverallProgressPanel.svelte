<script lang="ts">
  import ProgressBar from '../atoms/ProgressBar.svelte';

  let { completed, total }: { completed: number; total: number } = $props();
  
  let percentage = $derived(total > 0 ? Math.round((completed / total) * 100) : 0);
</script>

<section class="panel overall-progress">
  <header class="plain-header">
    <img src="/assets/widget/icons/leaf-icon.png" alt="" class="header-icon" />
    <h2>OVERALL PROGRESS</h2>
  </header>
  
  <div class="panel-body">
    <ProgressBar percentage="{percentage}%" label="{percentage}%" />
    <div class="milestone-count">
      <span>{completed} of {total} milestones completed</span>
    </div>
  </div>
</section>

<style>
  .panel {
    background: #fffdf8;
    border: 1px solid #d4cdbd;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .plain-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 14px 0;
  }
  .header-icon {
    width: 16px;
    height: 16px;
    object-fit: contain;
    image-rendering: pixelated;
  }
  .plain-header h2 {
    margin: 0;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    font-weight: 700;
  }
  .panel-body {
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .milestone-count {
    color: #0a65a2;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    text-align: right;
  }
</style>
