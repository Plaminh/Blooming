<script lang="ts">
  import ProgressBar from '../atoms/ProgressBar.svelte';
  import GoalsPanelHeader from '../atoms/GoalsPanelHeader.svelte';

  let { completed, total }: { completed: number; total: number } = $props();
  
  let percentage = $derived(total > 0 ? Math.round((completed / total) * 100) : 0);
</script>

<section class="panel overall-progress">
  <GoalsPanelHeader title="OVERALL PROGRESS" />
  
  <div class="panel-body">
    <div class="milestone-count">{completed} / {total} milestones</div>
    <ProgressBar percentage="{percentage}%" label="{percentage}%" />
  </div>
</section>

<style>
  .panel {
    height: 110px;
    flex: 0 0 110px;
    background: #fffdf8;
    border: 1px solid #24788c;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .panel-body {
    padding: 6px 12px 10px;
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  .milestone-count {
    color: #0a65a2;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    text-align: left;
  }
</style>
