<script lang="ts">
  import DesktopTitleBar from '$lib/shared/components/organisms/DesktopTitleBar.svelte';
  import AppSidebar from '$lib/shared/components/organisms/AppSidebar.svelte';
  import MyGoalsPanel from '$lib/features/goals/components/organisms/MyGoalsPanel.svelte';
  import GoalDetailsPanel from '$lib/features/goals/components/organisms/GoalDetailsPanel.svelte';
  import GoalsRightRail from '$lib/features/goals/components/organisms/GoalsRightRail.svelte';
  import FallbackDialog from '$lib/shared/components/molecules/FallbackDialog.svelte';
  import { FIXTURE_GOALS } from '$lib/features/goals/models';

  let selectedGoalId = $state(FIXTURE_GOALS[0].id);
  let showFallback = $state(false);

  let selectedGoal = $derived(FIXTURE_GOALS.find(g => g.id === selectedGoalId) || null);

  function handleAction() {
    showFallback = true;
  }
</script>

<div class="app-container">
  <DesktopTitleBar />
  <div class="main-layout">
    <AppSidebar activeRoute="GOALS" />
    <main class="goals-content">
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
    </main>
  </div>
</div>

<FallbackDialog 
  isOpen={showFallback} 
  onClose={() => (showFallback = false)} 
/>

<style>
  .app-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #eef8f6;
    overflow: hidden;
  }
  .main-layout {
    display: flex;
    flex: 1;
    min-height: 0;
  }
  .goals-content {
    flex: 1;
    display: grid;
    grid-template-columns: 320px minmax(400px, 1fr) 280px;
    gap: 12px;
    padding: 16px 20px 20px;
    height: 100%;
    overflow: hidden;
  }
  .col-my-goals, .col-goal-details, .col-right-rail {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
  }
</style>
