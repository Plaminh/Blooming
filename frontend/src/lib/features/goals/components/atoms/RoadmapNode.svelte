<script lang="ts">
  import type { MilestoneStatus } from '../../models';

  let {
    number,
    status,
    isLast,
    variant = 'default'
  }: {
    number: number;
    status: MilestoneStatus;
    isLast: boolean;
    variant?: 'default' | 'draft';
  } = $props();

  let nodeClass = $derived.by(() => {
    if (status === 'Completed') return 'node-completed';
    if (status === 'In progress') return 'node-in-progress';
    return 'node-not-started';
  });
</script>

<div class="roadmap-node-container" class:last={isLast} class:draft={variant === 'draft'}>
  <div class="node {nodeClass}">
    {number}
  </div>
  {#if !isLast}
    <div class="connector {nodeClass}"></div>
  {/if}
</div>

<style>
  .roadmap-node-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 55px;
    height: calc(100% + 21px);
  }
  .roadmap-node-container.last { height: 100%; }
  .roadmap-node-container.draft { height: 100%; }
  .node {
    width: 55px;
    height: 55px;
    flex: 0 0 55px;
    border: 1px solid #2e7c54;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-family: var(--bloom-body-font);
    font-size: 25px;
    font-weight: 700;
    z-index: 2;
  }
  .node-completed {
    background: #469a61;
  }
  .node-in-progress {
    background: #41965e;
  }
  .node-not-started {
    background: #90a5aa;
    border-color: #697f86;
  }
  .connector {
    width: 5px;
    flex: 1;
    min-height: 20px;
  }
  .connector.node-completed {
    background: linear-gradient(#469a61, #41965e);
  }
  .connector.node-in-progress {
    background: linear-gradient(#41965e, #90a5aa);
  }
  .connector.node-not-started {
    background: #90a5aa;
  }
</style>
