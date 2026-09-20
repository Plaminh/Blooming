<script lang="ts">
  import { onMount } from 'svelte';
  import { desktop } from '$lib/platform/desktopWindow';
  import { mrBloomStore } from '../../stores/mrBloomStore';
  import MrBloomConversationPanel from './MrBloomConversationPanel.svelte';
  import LiveDraftPlaceholder from './LiveDraftPlaceholder.svelte';
  import PlanDraftPreview from './PlanDraftPreview.svelte';
  import TodayDraftPreview from './TodayDraftPreview.svelte';
  import TimelineDraftPreview from './TimelineDraftPreview.svelte';
  onMount(() => {
    let unlisten = () => {};
    void mrBloomStore.restoreLatestSession();
    desktop.onProactiveNudge(nudge => mrBloomStore.receiveNudge(nudge)).then(value => unlisten = value);
    return () => unlisten();
  });
</script>

<div class="planning-workspace" class:has-draft={$mrBloomStore.previewMode !== 'placeholder'}>
  <div class="left-panel">
    <MrBloomConversationPanel />
  </div>
  <div class="right-panel">
    {#if $mrBloomStore.previewMode === 'placeholder'}
      <LiveDraftPlaceholder />
    {:else if $mrBloomStore.previewMode === 'roadmap'}
      <PlanDraftPreview />
    {:else if $mrBloomStore.previewMode === 'today'}
      <TodayDraftPreview />
    {:else if $mrBloomStore.previewMode === 'timeline'}
      <TimelineDraftPreview />
    {/if}
  </div>
</div>

<style>
  .planning-workspace {
    display: grid;
    width: 100%;
    height: 100%;
    min-width: 0;
    min-height: 0;
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
    gap: 10px;
    padding: 10px 8px 15px 13px;
    background: #f8f3e7;
  }

  .planning-workspace.has-draft {
    padding-top: 14px;
    padding-bottom: 9px;
  }

  .left-panel, .right-panel {
    display: flex;
    min-width: 0;
    min-height: 0;
    flex-direction: column;
    border: 2px solid #c9c3b5;
    border-radius: 6px;
    background: rgba(255, 253, 247, 0.72);
    overflow: hidden;
  }
</style>
