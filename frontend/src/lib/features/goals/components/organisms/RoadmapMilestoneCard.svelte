<script lang="ts">
  import type { Milestone } from '../../models';
  import GoalStatusBadge from '../atoms/GoalStatusBadge.svelte';
  import TargetDateLabel from '../atoms/TargetDateLabel.svelte';

  let { milestone, onUpdateMilestone }: { 
    milestone: Milestone, 
    onUpdateMilestone?: (id: string, updates: any) => void 
  } = $props();

  function handleStatusUpdate() {
    const newStatus = prompt("New status (PENDING, IN_PROGRESS, COMPLETED, SKIPPED, CANCELLED):", milestone.status);
    if (newStatus && onUpdateMilestone) {
        onUpdateMilestone(milestone.id, { status: newStatus });
    }
  }

  function handleDateUpdate() {
    const newDate = prompt("New Target Date (YYYY-MM-DD):", milestone.due_at || '');
    if (newDate !== null && onUpdateMilestone) {
        onUpdateMilestone(milestone.id, { due_at: newDate ? new Date(newDate).toISOString() : null });
    }
  }
</script>

<div class="milestone-card" class:completed={milestone.status === 'COMPLETED'}>
  <h4>{milestone.title}</h4>
  <p>{milestone.description}</p>
  <div class="meta-row">
    <button class="invisible-button" onclick={handleDateUpdate}>
        <TargetDateLabel date={milestone.due_at} />
    </button>
    <button class="invisible-button" onclick={handleStatusUpdate}>
        <GoalStatusBadge status={milestone.status} />
    </button>
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
  .invisible-button {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
  }
</style>
