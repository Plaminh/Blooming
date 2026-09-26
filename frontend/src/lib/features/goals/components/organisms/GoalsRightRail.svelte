<script lang="ts">
  import type { Goal, Milestone } from '../../models';
  import NextMilestonePanel from './NextMilestonePanel.svelte';
  import OverallProgressPanel from './OverallProgressPanel.svelte';
  import GoalsActionGroup from '../molecules/GoalsActionGroup.svelte';
  import DueRemindersPanel from './DueRemindersPanel.svelte';
  import { goalsStore } from '../../stores/goalsStore';

  let { goal, onRefine }: { goal: Goal | null; onRefine: () => void; } = $props();

  let nextMilestone = $derived.by(() => {
    if (!goal || goal.milestones.length === 0) return null;
    return goal.milestones.find((m) => m.status === 'PENDING' || m.status === 'IN_PROGRESS') || null;
  });

  let completedCount = $derived(goal ? goal.milestones.filter(m => m.status === 'COMPLETED').length : 0);
  let totalCount = $derived(goal ? goal.milestones.length : 0);
</script>

<div class="right-rail">
  <div class="top-section">
    {#if goal}
      <div class="panels-group">
        {#if $goalsStore.dueReminders.length > 0}
            <DueRemindersPanel 
                reminders={$goalsStore.dueReminders} 
                onAction={(id, action, date) => goalsStore.executeReminderAction(id, action, date)} 
            />
        {/if}
        <NextMilestonePanel milestone={nextMilestone} daysLeft={nextMilestone ? 17 : undefined} />
        <OverallProgressPanel completed={completedCount} total={totalCount} />
      </div>
      
      <GoalsActionGroup {onRefine} />
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
