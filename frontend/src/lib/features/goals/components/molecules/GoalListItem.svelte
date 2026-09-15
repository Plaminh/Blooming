<script lang="ts">
  import type { Goal } from '../../models';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { goal, selected, onSelect }: { goal: Goal; selected: boolean; onSelect: (id: string) => void } = $props();
</script>

<button class="goal-item {selected ? 'selected' : ''}" onclick={() => onSelect(goal.id)}>
  <div class="icon-wrap">
    {#if goal.iconRef === 'leaf'}
      <img src="/assets/widget/icons/leaf-icon.png" alt="" />
    {:else}
      <AppIcon name={goal.iconRef === 'book' ? 'book' : 'shoe'} scale={1.85} />
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
    min-height: 97px;
    padding: 11px 12px;
    background: #fffdf8;
    border: 1px solid #dcd7ca;
    border-radius: 6px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 10px;
    gap: 12px;
  }
  .goal-item.selected {
    min-height: 100px;
    background: #dff1fa;
    border-color: #a4d8f1;
  }
  .icon-wrap {
    width: 45px;
    height: 58px;
    flex: 0 0 45px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .icon-wrap img {
    width: 54px;
    height: 54px;
    object-fit: contain;
    image-rendering: pixelated;
    transform: translateX(-6px) scale(1.35);
  }
  .content {
    flex: 1;
    min-width: 0;
  }
  .content h3 {
    margin: 0 0 4px 0;
    font-family: var(--bloom-display-font);
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.055em;
    line-height: 1.25;
    color: #064b91;
  }
  .content p {
    margin: 0;
    font-family: var(--bloom-body-font);
    font-size: 17px;
    color: #1479ab;
    line-height: 1.3;
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
