<script lang="ts">
  import type { Goal } from '../../models';
  import TargetDateLabel from '../atoms/TargetDateLabel.svelte';
  import RoadmapTimeline from './RoadmapTimeline.svelte';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { goal }: { goal: Goal | null } = $props();
</script>

<section class="panel goal-details">
  <header class="panel-header">
    <img src="/assets/widget/icons/leaf-icon.png" alt="" class="header-icon" />
    <h2 id="goal-details-heading">GOAL DETAILS</h2>
  </header>
  
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
    background: #f7f6ed;
    border: 1px solid #d4cdbd;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }
  .panel-header {
    background: linear-gradient(#3998ad, #24859f);
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .header-icon {
    width: 20px;
    height: 20px;
    object-fit: contain;
    image-rendering: pixelated;
  }
  .panel-header h2 {
    margin: 0;
    color: white;
    font-family: var(--bloom-body-font);
    font-size: 17px;
    font-weight: 700;
  }
  .panel-body {
    padding: 24px;
    flex: 1;
    overflow-y: auto;
  }
  .goal-summary {
    display: flex;
    gap: 20px;
    margin-bottom: 30px;
    align-items: flex-start;
  }
  .summary-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .summary-icon img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    image-rendering: pixelated;
  }
  .summary-text {
    flex: 1;
  }
  .summary-text h3 {
    margin: 0 0 6px 0;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 24px;
    font-weight: 700;
  }
  .summary-text p {
    margin: 0;
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 16px;
    line-height: 1.4;
  }
  .target-date-box {
    border: 1px solid #dcd7ca;
    background: #fffdf8;
    padding: 10px 14px;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    min-width: 110px;
  }
  .box-label {
    color: #0c61a1;
    font-family: var(--bloom-body-font);
    font-size: 12px;
  }
  .roadmap-heading {
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 19px;
    font-weight: 700;
    margin: 0 0 20px 0;
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
