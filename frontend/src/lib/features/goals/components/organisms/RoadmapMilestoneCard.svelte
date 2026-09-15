<script lang="ts">
  import type { Milestone } from '../../models';
  import GoalStatusBadge from '../atoms/GoalStatusBadge.svelte';
  import TargetDateLabel from '../atoms/TargetDateLabel.svelte';

  let { milestone }: { milestone: Milestone } = $props();
</script>

<div class="milestone-card" class:completed={milestone.status === 'Completed'}>
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
    min-height: 108px;
    padding: 8px 12px;
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  .milestone-card.completed { background: #f2faef; border-color: #bfd8c2; }
  h4 {
    margin: 0 0 3px 0;
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.055em;
    line-height: 1.2;
  }
  p {
    margin: 0 0 4px 0;
    color: #0a65a2;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    line-height: 1.25;
  }
  .meta-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
  }
</style>
