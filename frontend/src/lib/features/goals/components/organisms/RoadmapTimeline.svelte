<script lang="ts">
  import type { Milestone } from '../../models';
  import RoadmapNode from '../atoms/RoadmapNode.svelte';
  import RoadmapMilestoneCard from './RoadmapMilestoneCard.svelte';

  let { milestones }: { milestones: Milestone[] } = $props();
</script>

<div class="roadmap-timeline">
  {#if milestones.length > 0}
    {#each milestones as milestone, index (milestone.id)}
      <div class="timeline-row">
        <div class="node-col">
          <RoadmapNode
            number={index + 1}
            status={milestone.status}
            isLast={index === milestones.length - 1}
          />
        </div>
        <div class="card-col">
          <RoadmapMilestoneCard {milestone} />
        </div>
      </div>
    {/each}
  {:else}
    <p class="empty-state">No milestones defined yet.</p>
  {/if}
</div>

<style>
  .roadmap-timeline {
    display: flex;
    flex-direction: column;
    gap: 21px;
  }
  .timeline-row {
    display: flex;
    min-height: 142px;
    gap: 14px;
    /* Ensure the row stretches so the connector can reach the next row */
    align-items: stretch;
  }
  .timeline-row:first-child {
    margin-bottom: 7px;
  }
  .timeline-row:nth-child(3) {
    transform: translateY(-2px);
  }
  .timeline-row:nth-child(4) {
    transform: translateY(-1px);
  }
  .node-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 55px;
    flex: 0 0 55px;
    transform: translateY(3px);
  }
  .card-col {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  .timeline-row:first-child .card-col {
    transform: translateY(-2px);
  }
  .empty-state {
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    padding: 20px;
    text-align: center;
  }
</style>
