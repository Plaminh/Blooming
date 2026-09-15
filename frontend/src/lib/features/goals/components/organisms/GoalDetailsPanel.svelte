<script lang="ts">
  import type { Goal } from '../../models';
  import TargetDateLabel from '../atoms/TargetDateLabel.svelte';
  import RoadmapTimeline from './RoadmapTimeline.svelte';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import GoalsPanelHeader from '../atoms/GoalsPanelHeader.svelte';

  let { goal }: { goal: Goal | null } = $props();
</script>

<section class="panel goal-details">
  <GoalsPanelHeader title="GOAL DETAILS" id="goal-details-heading" icon />
  
  <div class="panel-body">
    {#if goal}
      <div class="goal-summary">
        <div class="summary-icon">
          {#if goal.iconRef === 'leaf'}
            <img src="/assets/widget/icons/leaf-icon.png" alt="" />
          {:else}
            <AppIcon name={goal.iconRef as any} scale={1.1} />
          {/if}
        </div>
        <div class="summary-text">
          <h3>{goal.title}</h3>
          <p>{goal.description}</p>
        </div>
        <div class="target-date-box">
          <span class="box-label">Target date</span>
          <TargetDateLabel date={goal.targetDate} />
        </div>
      </div>
      
      <h3 class="roadmap-heading">ROADMAP</h3>
      <RoadmapTimeline milestones={goal.milestones} />
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
    padding: 21px 14px 20px 21px;
    flex: 1;
    overflow-y: auto;
  }
  .goal-summary {
    display: flex;
    min-height: 77px;
    gap: 18px;
    margin-bottom: 23px;
    align-items: flex-start;
  }
  .summary-icon {
    width: 54px;
    height: 58px;
    flex: 0 0 54px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .summary-icon img {
    width: 54px;
    height: 54px;
    object-fit: contain;
    image-rendering: pixelated;
    transform: scale(1.5);
  }
  .summary-text {
    flex: 1;
    min-width: 0;
  }
  .summary-text h3 {
    margin: 0 0 6px 0;
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.06em;
  }
  .summary-text p {
    margin: 0;
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 17px;
    line-height: 1.4;
    white-space: nowrap;
  }
  .target-date-box {
    border: 1px solid #dcd7ca;
    background: #fffdf8;
    width: 128px;
    height: 76px;
    flex: 0 0 128px;
    padding: 10px 8px;
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
    font-size: 13px;
  }
  .roadmap-heading {
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.055em;
    margin: 0 0 19px 0;
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
