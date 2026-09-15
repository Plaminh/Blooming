<script lang="ts">
  import type { Milestone } from '../../models';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import GoalsPanelHeader from '../atoms/GoalsPanelHeader.svelte';
  import TargetDateLabel from '../atoms/TargetDateLabel.svelte';

  let { milestone, daysLeft }: { milestone: Milestone | null; daysLeft?: number } = $props();
</script>

<section class="panel next-milestone">
  <GoalsPanelHeader title="NEXT MILESTONE" icon />
  
  <div class="panel-body">
    {#if milestone}
      <div class="milestone-main">
        <div class="document-icon"><AppIcon name="document" scale={1.85} /></div>
        <div class="milestone-info">
          <h3>{milestone.title}</h3>
          <p>{milestone.summary ?? milestone.description}</p>
        </div>
      </div>
      <div class="milestone-meta">
        <TargetDateLabel date={milestone.date} />
        {#if daysLeft !== undefined}
          <div class="days-left"><span>In {daysLeft} days</span></div>
        {/if}
      </div>
    {:else}
      <p class="empty-state">No upcoming milestones.</p>
    {/if}
  </div>
</section>

<style>
  .panel {
    height: 225px;
    flex: 0 0 225px;
    background: #fffdf8;
    border: 1px solid #24788c;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .panel-body {
    min-height: 0;
    padding: 20px 16px 18px 28px;
    display: flex;
    flex: 1;
    flex-direction: column;
    justify-content: space-between;
  }
  .milestone-main {
    display: flex;
    align-items: flex-start;
    gap: 24px;
  }
  .document-icon {
    display: grid;
    width: 47px;
    height: 54px;
    flex: 0 0 47px;
    place-items: center;
    color: #0b657e;
  }
  .milestone-info {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }
  .milestone-info h3 {
    margin: 0;
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.055em;
  }
  .milestone-info p {
    margin: 0;
    color: #0a65a2;
    font-family: var(--bloom-body-font);
    font-size: 19px;
    line-height: 1.35;
  }
  .milestone-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .days-left {
    background: #c3e5f5;
    color: #064b91;
    padding: 7px 13px;
    border-radius: 4px;
    font-family: var(--bloom-body-font);
    font-size: 16px;
    font-weight: 700;
  }
  .empty-state {
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    margin: 0;
  }
</style>
