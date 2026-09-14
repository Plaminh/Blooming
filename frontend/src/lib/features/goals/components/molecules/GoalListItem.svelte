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
      <AppIcon name={goal.iconRef as any} scale={0.7} />
    {/if}
  </div>
  <div class="content">
    <h3>{goal.title}</h3>
    <p>{goal.description}</p>
  </div>
  <div class="arrow">
    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M1.5 1L6.5 6L1.5 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>
</button>

<style>
  .goal-item {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 16px 14px;
    background: #fffdf8;
    border: 1px solid #dcd7ca;
    border-radius: 6px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 8px;
    gap: 14px;
  }
  .goal-item.selected {
    background: #dff1fa;
    border-color: #a4d8f1;
  }
  .icon-wrap {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .icon-wrap img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    image-rendering: pixelated;
  }
  .content {
    flex: 1;
    min-width: 0;
  }
  .content h3 {
    margin: 0 0 4px 0;
    font-family: var(--bloom-body-font);
    font-size: 16px;
    font-weight: 700;
    color: #064b91;
  }
  .content p {
    margin: 0;
    font-family: var(--bloom-body-font);
    font-size: 13px;
    color: #1479ab;
    line-height: 1.3;
  }
  .arrow {
    color: #064b91;
  }
</style>
