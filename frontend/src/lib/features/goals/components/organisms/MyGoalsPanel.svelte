<script lang="ts">
  import type { Goal } from '../../models';
  import GoalListItem from '../molecules/GoalListItem.svelte';

  let { goals, selectedGoalId, onSelect, onCreateGoal }: { goals: Goal[]; selectedGoalId: string; onSelect: (id: string) => void; onCreateGoal: () => void; } = $props();
</script>

<section class="panel my-goals">
  <header class="panel-header">
    <h2 id="my-goals-heading">MY GOALS</h2>
  </header>
  
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
    background: #e6f6f3;
    border: 1px solid #cfcebe;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }
  .panel-header {
    background: linear-gradient(#3998ad, #24859f);
    padding: 10px 14px;
  }
  .panel-header h2 {
    margin: 0;
    color: white;
    font-family: var(--bloom-body-font);
    font-size: 17px;
    font-weight: 700;
  }
  .panel-body {
    padding: 14px;
    flex: 1;
    overflow-y: auto;
  }
  .btn-create {
    width: 100%;
    background: linear-gradient(#4bad6a, #269553);
    border: 1px solid #1a7847;
    border-radius: 5px;
    color: white;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    font-weight: 700;
    padding: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    cursor: pointer;
    margin-bottom: 16px;
  }
  .icon-plus {
    font-size: 20px;
    line-height: 1;
  }
  .goals-list {
    display: flex;
    flex-direction: column;
  }
</style>
