<script lang="ts">
  import type { Goal, Milestone } from '../../models';
  import NextMilestonePanel from './NextMilestonePanel.svelte';
  import OverallProgressPanel from './OverallProgressPanel.svelte';
  import GoalsActionGroup from '../molecules/GoalsActionGroup.svelte';
  import GardenPanel from '$lib/shared/components/organisms/GardenPanel.svelte';

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

  <div class="bottom-section">
    <GardenPanel />
  </div>
</div>

<style>
  .right-rail {
    display: flex;
    flex-direction: column;
    height: 100%;
    justify-content: space-between;
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
  .bottom-section {
    margin-top: auto;
    height: 270px;
    margin-bottom: 8px;
  }

  .bottom-section :global(.garden) {
    height: 100%;
    grid-template-rows: 39px 1fr 58px;
  }

  .bottom-section :global(.garden .panel-strip) {
    height: 39px;
  }

  .bottom-section :global(.garden .garden-footer) {
    font-size: 16px;
  }

  .bottom-section :global(.garden .garden-scene) {
    --garden-bush-scale: 3;
  }

  .bottom-section :global(.garden .flower) {
    bottom: 24px;
    height: 45px;
  }

  .bottom-section :global(.garden .flower::before) {
    width: 20px;
    height: 8px;
    top: 1px;
  }

  .bottom-section :global(.garden .flower::after) {
    content: '';
    position: absolute;
    left: 0;
    top: -6px;
    width: 7px;
    height: 20px;
    background: inherit;
  }

  .bottom-section :global(.garden .garden-footer span:last-child) {
    font-size: 18px;
  }
</style>
