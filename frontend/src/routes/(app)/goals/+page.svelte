<script lang="ts">
  import MyGoalsPanel from '$lib/features/goals/components/organisms/MyGoalsPanel.svelte';
  import GoalDetailsPanel from '$lib/features/goals/components/organisms/GoalDetailsPanel.svelte';
  import GoalsRightRail from '$lib/features/goals/components/organisms/GoalsRightRail.svelte';
  import FallbackDialog from '$lib/shared/components/molecules/FallbackDialog.svelte';
  import { overlayStore } from '$lib/shared/stores/overlayStore';
  import { goalsStore } from '$lib/features/goals/stores/goalsStore';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let selectedGoalId = $state<string | null>(null);
  let showFallback = $state(false);

  let selectedGoal = $derived($goalsStore.goals.find(g => g.id === selectedGoalId) || null);

  onMount(() => {
    goalsStore.loadGoals().then(() => {
        if ($goalsStore.goals.length > 0 && !selectedGoalId) {
            selectedGoalId = $goalsStore.goals[0].id;
        }
    });
    goalsStore.loadDueReminders();
  });

  function handleAction() {
    showFallback = true;
  }
  
  $effect(() => {
    overlayStore.set(goalsOverlay);
    return () => overlayStore.set(undefined);
  });
</script>

<svelte:head>
  <title>Goals - Blooming</title>
</svelte:head>

{#snippet goalsOverlay()}
  <FallbackDialog
    isOpen={showFallback}
    onClose={() => (showFallback = false)}
  />
{/snippet}

<div class="goals-content">
  <div class="col-my-goals">
    <MyGoalsPanel
      goals={$goalsStore.goals}
      {selectedGoalId}
      onSelect={(id) => (selectedGoalId = id)}
      onCreateGoal={() => {
        goto('/mr-bloom');
      }}
    />
  </div>
  <div class="col-goal-details">
    <GoalDetailsPanel 
      goal={selectedGoal} 
      onUpdateMilestone={(milestoneId, updates) => {
        if (selectedGoalId) goalsStore.updateMilestone(selectedGoalId, milestoneId, updates);
      }}
    />
  </div>
  <div class="col-right-rail">
    <GoalsRightRail
      goal={selectedGoal}
      onEdit={() => {
        if (selectedGoal) {
            const title = prompt("New Goal Title:", selectedGoal.title);
            if (title && selectedGoalId) goalsStore.updateGoal(selectedGoalId, { title });
        }
      }}
      onRefine={handleAction}
    />
  </div>
</div>

<style>
  .goals-content {
    display: grid;
    width: 100%;
    height: 100%;
    min-width: 0;
    min-height: 0;
    grid-template-columns: 270px 470px minmax(0, 1fr);
    gap: 10px;
    padding: 10px 10px 10px 12px;
    overflow: hidden;
    background: var(--bloom-surface-cream);
  }

  .col-my-goals,
  .col-goal-details,
  .col-right-rail {
    display: flex;
    min-width: 0;
    flex-direction: column;
    height: 100%;
    min-height: 0;
  }

</style>
