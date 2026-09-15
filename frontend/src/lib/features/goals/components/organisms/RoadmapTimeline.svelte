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
    gap: 8px;
  }
  .timeline-row {
    display: flex;
    min-height: 108px;
    gap: 10px;
    /* Ensure the row stretches so the connector can reach the next row */
    align-items: stretch;
  }
  .node-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 48px;
    flex: 0 0 48px;
  }
  .card-col {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  .empty-state {
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    padding: 20px;
    text-align: center;
  }
</style>
