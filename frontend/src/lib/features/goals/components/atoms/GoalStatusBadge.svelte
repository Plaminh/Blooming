<script lang="ts">
  import type { MilestoneStatus } from '../../models';
  let { status }: { status: MilestoneStatus } = $props();
</script>

<span class="goal-status-badge status-{status.toLowerCase().replace(/ /g, '-')}">
  {status}
</span>

<style>
  .goal-status-badge {
    display: inline-flex;
    align-items: center;
    min-height: 30px;
    padding: 3px 10px;
    border-radius: 4px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 500;
  }
  .status-completed {
    background: var(--bloom-goal-status-completed-bg);
    color: var(--bloom-goal-status-completed-text);
  }
  .status-in-progress {
    background: var(--bloom-goal-status-in-progress-bg);
    color: var(--bloom-goal-status-in-progress-text);
  }
  .status-not-started {
    background: var(--bloom-goal-status-not-started-bg);
    color: var(--bloom-goal-status-not-started-text);
  }
</style>
