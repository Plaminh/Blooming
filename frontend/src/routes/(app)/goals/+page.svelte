<script lang="ts">
  import MyGoalsPanel from '$lib/features/goals/components/organisms/MyGoalsPanel.svelte';
  import GoalDetailsPanel from '$lib/features/goals/components/organisms/GoalDetailsPanel.svelte';
  import GoalsRightRail from '$lib/features/goals/components/organisms/GoalsRightRail.svelte';
  import FallbackDialog from '$lib/shared/components/molecules/FallbackDialog.svelte';
  import { FIXTURE_GOALS } from '$lib/features/goals/models';
  import { overlayStore } from '$lib/shared/stores/overlayStore';

  let selectedGoalId = $state(FIXTURE_GOALS[0].id);
  let showFallback = $state(false);

  let selectedGoal = $derived(FIXTURE_GOALS.find(g => g.id === selectedGoalId) || null);

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
      goals={FIXTURE_GOALS}
      {selectedGoalId}
      onSelect={(id) => (selectedGoalId = id)}
      onCreateGoal={handleAction}
    />
  </div>
  <div class="col-goal-details">
    <GoalDetailsPanel goal={selectedGoal} />
  </div>
  <div class="col-right-rail">
    <GoalsRightRail
      goal={selectedGoal}
      onEdit={handleAction}
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
