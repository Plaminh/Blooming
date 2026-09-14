<script lang="ts">
  import type { MilestoneStatus } from '../../models';

  let { number, status, isLast }: { number: number; status: MilestoneStatus; isLast: boolean } = $props();

  let nodeClass = $derived.by(() => {
    if (status === 'Completed') return 'node-completed';
    if (status === 'In progress') return 'node-in-progress';
    return 'node-not-started';
  });
</script>

<div class="roadmap-node-container">
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
    width: 30px;
    height: 100%;
  }
  .node {
    width: 28px;
    height: 28px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-family: var(--bloom-body-font);
    font-size: 16px;
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
  }
  .connector {
    width: 4px;
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
