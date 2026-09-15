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
    gap: 14px;
  }
  .panels-group {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .bottom-section {
    margin-top: auto;
    height: 309px;
    margin-bottom: 24px;
  }

  .bottom-section :global(.garden) {
    height: 100%;
    grid-template-rows: 43px 1fr 67px;
  }

  .bottom-section :global(.garden .panel-strip) {
    height: 43px;
  }

  .bottom-section :global(.garden .garden-footer) {
    font-size: 18px;
  }

  .bottom-section :global(.garden .panel-strip img) {
    transform: scale(1.7);
  }

  .bottom-section :global(.garden .sky) {
    bottom: 22px;
  }

  .bottom-section :global(.garden .bushes) {
    left: -100%;
    bottom: -69px;
    width: 300%;
  }

  .bottom-section :global(.garden .ground) {
    height: 24px;
    background:
      repeating-linear-gradient(90deg, rgba(96, 107, 105, 0.2) 0 2px, transparent 2px 32px),
      repeating-linear-gradient(90deg, #dad7cc 0 24px, #eee9dc 24px 48px);
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

  .bottom-section :global(.garden .garden-footer img.app-icon) {
    width: 50px !important;
    transform: scale(1.5);
  }

  .bottom-section :global(.garden .garden-footer span:last-child) {
    font-size: 20px;
  }
</style>
