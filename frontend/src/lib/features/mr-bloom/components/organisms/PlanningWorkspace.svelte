<script lang="ts">
  import { mrBloomStore } from '../../stores/mrBloomStore';
  import MrBloomConversationPanel from './MrBloomConversationPanel.svelte';
  import LiveDraftPlaceholder from './LiveDraftPlaceholder.svelte';
  import PlanDraftPreview from './PlanDraftPreview.svelte';
  import TodayDraftPreview from './TodayDraftPreview.svelte';
  import TimelineDraftPreview from './TimelineDraftPreview.svelte';
</script>

<div class="planning-workspace">
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
    display: flex;
    width: 100%;
    height: 100%;
    gap: 16px;
    padding: 16px;
    box-sizing: border-box;
    background: #fdfaf3; /* Based on reference */
  }

  .left-panel, .right-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #fffbf2;
    border: 1px solid #cfc9b9;
    border-radius: 6px;
    overflow: hidden;
  }
  
  .left-panel {
    flex: 0 0 45%;
  }
  
  .right-panel {
    flex: 1;
  }
</style>
