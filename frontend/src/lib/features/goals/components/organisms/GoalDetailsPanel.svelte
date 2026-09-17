<script lang="ts">
  import type { Goal } from '../../models';
  import TargetDateLabel from '../atoms/TargetDateLabel.svelte';
  import RoadmapTimeline from './RoadmapTimeline.svelte';
  import AppIcon, { type IconName } from '$lib/shared/components/atoms/AppIcon.svelte';
  import GoalsPanelHeader from '../atoms/GoalsPanelHeader.svelte';

  let { goal, onAddMilestone, onUpdateMilestone }: { 
    goal: Goal | null, 
    onAddMilestone?: () => void,
    onUpdateMilestone?: (milestoneId: string, updates: any) => void 
  } = $props();
</script>

<section class="panel goal-details">
  <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #dcd7ca;">
    <GoalsPanelHeader title="GOAL DETAILS" id="goal-details-heading" />
    {#if onAddMilestone}
      <button style="margin-right: 10px; cursor: pointer;" onclick={onAddMilestone}>+ Milestone</button>
    {/if}
  </div>
  
  <div class="panel-body">
    {#if goal}
      <div class="goal-summary">
        {#if goal.iconRef !== 'leaf' && goal.iconRef !== 'sprout'}
          <div class="summary-icon">
            <AppIcon name={goal.iconRef as IconName} size="goal-detail" />
          </div>
        {/if}
        <div class="summary-text">
          <h3>{goal.title}</h3>
          <p>{goal.description}</p>
        </div>
        <div class="target-date-box">
          <span class="box-label">Target date</span>
          <TargetDateLabel date={goal.target_date} />
        </div>
      </div>
      
      <h3 class="roadmap-heading">ROADMAP</h3>
      <RoadmapTimeline milestones={goal.milestones} {onUpdateMilestone} />
    {:else}
      <div class="empty-state">
        <p>No goal selected.</p>
      </div>
    {/if}
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
    padding: 14px 12px 12px 14px;
    flex: 1;
    overflow-y: auto;
  }
  .goal-summary {
    display: flex;
    min-height: 64px;
    gap: 12px;
    margin-bottom: 12px;
    align-items: center;
  }
  .summary-icon {
    color: #0872ae;
    width: var(--bloom-icon-goal-detail);
    height: var(--bloom-icon-goal-detail);
    flex: 0 0 var(--bloom-icon-goal-detail);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .summary-text {
    flex: 1;
    min-width: 0;
  }
  .summary-text h3 {
    margin: 0 0 4px 0;
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.06em;
  }
  .summary-text p {
    margin: 0;
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    line-height: 1.3;
    white-space: nowrap;
  }
  .target-date-box {
    border: 1px solid #dcd7ca;
    background: #fffdf8;
    width: 116px;
    height: 62px;
    flex: 0 0 116px;
    padding: 6px 7px;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    box-sizing: border-box;
  }
  .box-label {
    color: #0c61a1;
    font-family: var(--bloom-body-font);
    font-size: 12px;
  }
  .roadmap-heading {
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 23px;
    font-weight: 800;
    letter-spacing: -0.055em;
    margin: 0 0 8px 0;
  }
  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 16px;
  }
</style>
