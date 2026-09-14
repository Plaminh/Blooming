<script lang="ts">
  import type { Milestone } from '../../models';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { milestone, daysLeft }: { milestone: Milestone | null; daysLeft?: number } = $props();
</script>

<section class="panel next-milestone">
  <header class="plain-header">
    <AppIcon name="calendar" scale={0.75} />
    <h2>NEXT MILESTONE</h2>
  </header>
  
  <div class="panel-body">
    {#if milestone}
      <div class="milestone-info">
        <h3>{milestone.title}</h3>
        <span class="date">{milestone.date}</span>
      </div>
      {#if daysLeft !== undefined}
        <div class="days-left">
          <span>In {daysLeft} days</span>
        </div>
      {/if}
    {:else}
      <p class="empty-state">No upcoming milestones.</p>
    {/if}
  </div>
</section>

<style>
  .panel {
    background: #fffdf8;
    border: 1px solid #d4cdbd;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .plain-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 14px 0;
  }
  .plain-header h2 {
    margin: 0;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    font-weight: 700;
  }
  .panel-body {
    padding: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .milestone-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .milestone-info h3 {
    margin: 0;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 16px;
    font-weight: 700;
  }
  .date {
    color: #0a65a2;
    font-family: var(--bloom-body-font);
    font-size: 14px;
  }
  .days-left {
    background: #c3e5f5;
    color: #064b91;
    padding: 4px 10px;
    border-radius: 4px;
    font-family: var(--bloom-body-font);
    font-size: 13px;
    font-weight: 700;
  }
  .empty-state {
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    margin: 0;
  }
</style>
