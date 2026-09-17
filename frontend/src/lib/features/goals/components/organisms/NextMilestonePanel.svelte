<script lang="ts">
  import type { Milestone } from '../../models';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import GoalsPanelHeader from '../atoms/GoalsPanelHeader.svelte';
  import TargetDateLabel from '../atoms/TargetDateLabel.svelte';

  let { milestone, daysLeft }: { milestone: Milestone | null; daysLeft?: number } = $props();
</script>

<section class="panel next-milestone">
  <GoalsPanelHeader title="NEXT MILESTONE" />
  
  <div class="panel-body">
    {#if milestone}
      <div class="milestone-main">
        <div class="document-icon"><AppIcon name="document" size="roadmap-milestone" /></div>
        <div class="milestone-info">
          <h3>{milestone.title}</h3>
          <p>{milestone.summary ?? milestone.description}</p>
        </div>
      </div>
      <div class="milestone-meta">
        <TargetDateLabel date={milestone.due_at} />
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
    height: 184px;
    flex: 0 0 184px;
    background: #fffdf8;
    border: 1px solid #24788c;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .panel-body {
    min-height: 0;
    padding: 13px 12px 12px 16px;
    display: flex;
    flex: 1;
    flex-direction: column;
    justify-content: space-between;
  }
  .milestone-main {
    display: flex;
    align-items: flex-start;
    gap: 14px;
  }
  .document-icon {
    display: grid;
    width: var(--bloom-icon-roadmap-milestone);
    height: var(--bloom-icon-roadmap-milestone);
    flex: 0 0 var(--bloom-icon-roadmap-milestone);
    align-self: center;
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
    font-size: 19px;
    font-weight: 800;
    letter-spacing: -0.055em;
  }
  .milestone-info p {
    margin: 0;
    color: #0a65a2;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    line-height: 1.3;
  }
  .milestone-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .days-left {
    background: #c3e5f5;
    color: #064b91;
    padding: 5px 9px;
    border-radius: 4px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 700;
  }
  .empty-state {
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    margin: 0;
  }
</style>
