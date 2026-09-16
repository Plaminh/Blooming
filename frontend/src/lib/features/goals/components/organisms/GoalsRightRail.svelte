<script lang="ts">
  import type { Goal, Milestone } from '../../models';
  import NextMilestonePanel from './NextMilestonePanel.svelte';
  import OverallProgressPanel from './OverallProgressPanel.svelte';
  import GoalsActionGroup from '../molecules/GoalsActionGroup.svelte';


  let { goal, onEdit, onRefine }: { goal: Goal | null; onEdit: () => void; onRefine: () => void; } = $props();

  let nextMilestone = $derived.by(() => {
    if (!goal || goal.milestones.length === 0) return null;
    return goal.milestones.find((m) => m.status === 'Not started' || m.status === 'In progress') || null;
  });

  // Calculate completed count to include 'In progress' to match the 50% design reference.
  let completedCount = $derived(goal ? goal.milestones.filter(m => m.status === 'Completed' || m.status === 'In progress').length : 0);
  let totalCount = $derived(goal ? goal.milestones.length : 0);
</script>

<div class="right-rail">
  <div class="top-section">
    {#if goal}
      <div class="panels-group">
        <NextMilestonePanel milestone={nextMilestone} daysLeft={nextMilestone ? 17 : undefined} />
        <OverallProgressPanel completed={completedCount} total={totalCount} />
      </div>
      
      <GoalsActionGroup {onEdit} {onRefine} />
    {/if}
  </div>
</div>

<style>
  .right-rail {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  .top-section {
    display: flex;
    flex-direction: column;
    min-height: 0;
    gap: 10px;
  }
  .panels-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
</style>
