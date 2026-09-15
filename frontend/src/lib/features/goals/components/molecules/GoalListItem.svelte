<script lang="ts">
  import type { Goal } from '../../models';
  import AppIcon, { type IconName } from '$lib/shared/components/atoms/AppIcon.svelte';

  let { goal, selected, onSelect }: { goal: Goal; selected: boolean; onSelect: (id: string) => void } = $props();
</script>

<button class="goal-item {selected ? 'selected' : ''}" onclick={() => onSelect(goal.id)}>
  <div class="icon-wrap">
    {#if goal.iconRef !== 'leaf' && goal.iconRef !== 'sprout'}
      <AppIcon name={goal.iconRef as IconName} size="goal-list" />
    {/if}
  </div>
  <div class="content">
    <h3>{goal.title}</h3>
    <p>{goal.description}</p>
  </div>
  <div class="arrow"><AppIcon name="chevron-right" scale={0.8} /></div>
</button>

<style>
  .goal-item {
    display: flex;
    align-items: center;
    width: 100%;
    min-height: 80px;
    padding: 8px 10px;
    background: #fffdf8;
    border: 1px solid #dcd7ca;
    border-radius: 6px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 6px;
    gap: 9px;
  }
  .goal-item.selected {
    min-height: 82px;
    background: #dff1fa;
    border-color: #a4d8f1;
  }
  .icon-wrap {
    width: var(--bloom-icon-goal-list);
    height: var(--bloom-icon-goal-list);
    flex: 0 0 var(--bloom-icon-goal-list);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .content {
    flex: 1;
    min-width: 0;
  }
  .content h3 {
    margin: 0 0 4px 0;
    font-family: var(--bloom-display-font);
    font-size: 17px;
    font-weight: 800;
    letter-spacing: -0.055em;
    line-height: 1.25;
    color: #064b91;
  }
  .content p {
    margin: 0;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    color: #1479ab;
    line-height: 1.25;
  }
  .arrow {
    display: grid;
    width: 16px;
    flex: 0 0 16px;
    place-items: center;
    color: #064b91;
  }

  .icon-wrap :global(.fallback-svg) {
    color: #0872ae;
  }
</style>
