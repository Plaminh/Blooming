<script lang="ts">
  import type { Goal } from '../../models';
  import GoalListItem from '../molecules/GoalListItem.svelte';
  import GoalsPanelHeader from '../atoms/GoalsPanelHeader.svelte';

  let { goals, selectedGoalId, onSelect, onCreateGoal }: { goals: Goal[]; selectedGoalId: string; onSelect: (id: string) => void; onCreateGoal: () => void; } = $props();
</script>

<section class="panel my-goals">
  <GoalsPanelHeader title="MY GOALS" id="my-goals-heading" />
  
  <div class="panel-body">
    <button class="btn-create" onclick={onCreateGoal}>
      <span class="icon-plus">+</span>
      CREATE GOAL WITH MR. BLOOM
    </button>
    
    <div class="goals-list" aria-labelledby="my-goals-heading">
      {#each goals as goal (goal.id)}
        <GoalListItem
          {goal}
          selected={goal.id === selectedGoalId}
          {onSelect}
        />
      {/each}
    </div>
  </div>
</section>

<style>
  .panel {
    background: rgba(255, 253, 247, 0.78);
    border: 1px solid #aab6aa;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }
  .panel-body {
    padding: 12px 13px;
    flex: 1;
    overflow-y: auto;
  }
  .my-goals :global(.goals-panel-header) {
    padding-left: 21px;
  }
  .btn-create {
    width: 100%;
    background: linear-gradient(#4bad6a, #269553);
    border: 1px solid #1a7847;
    border-radius: 5px;
    color: white;
    height: 55px;
    font-family: var(--bloom-display-font);
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.05em;
    padding: 0 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 11px;
    cursor: pointer;
    margin-bottom: 13px;
  }
  .icon-plus {
    font-family: var(--bloom-body-font);
    font-size: 34px;
    font-weight: 300;
    line-height: 1;
  }
  .goals-list {
    display: flex;
    flex-direction: column;
  }
</style>
