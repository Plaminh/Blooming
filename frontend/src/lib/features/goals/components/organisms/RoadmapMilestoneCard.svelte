<script lang="ts">
  import type { Milestone } from '../../models';
  import GoalStatusBadge from '../atoms/GoalStatusBadge.svelte';
  import TargetDateLabel from '../atoms/TargetDateLabel.svelte';

  let { milestone }: { milestone: Milestone } = $props();
</script>

<div class="milestone-card">
  <h4>{milestone.title}</h4>
  <p>{milestone.description}</p>
  <div class="meta-row">
    <TargetDateLabel date={milestone.date} />
    <GoalStatusBadge status={milestone.status} />
  </div>
</div>

<style>
  .milestone-card {
    background: #fffdf8;
    border: 1px solid #d9d5c8;
    border-radius: 6px;
    padding: 14px 16px;
    margin-bottom: 24px;
    flex: 1;
  }
  h4 {
    margin: 0 0 6px 0;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 16px;
    font-weight: 700;
  }
  p {
    margin: 0 0 12px 0;
    color: #0a65a2;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    line-height: 1.35;
  }
  .meta-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
</style>
