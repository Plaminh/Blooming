<script lang="ts">
  import { mrBloomStore, type TodayDraft } from '../../stores/mrBloomStore';
  import DraftReviewHeader from './DraftReviewHeader.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import DraftTaskSummary from '../molecules/DraftTaskSummary.svelte';
  
  let draft = $derived($mrBloomStore.activeDraft as TodayDraft);
  
  function handleGenerateTimeline() {
    mrBloomStore.generateTimeline();
  }
</script>

<div class="today-draft-preview">
  {#if draft && draft.type === 'today'}
    <DraftReviewHeader 
      type="TODAY" 
      title="Tasks Extracted" 
      subtitle="I've pulled out tasks based on your {draft.availability.totalHours} hour availability." 
    />
    
    <div class="content">
      <div class="tasks-list">
        {#each draft.tasks as task (task.id)}
          <DraftTaskSummary {task} />
        {/each}
      </div>
    </div>
    
    <DraftReviewActionBar 
      primaryLabel="Generate Timeline" 
      onPrimary={handleGenerateTimeline} 
    />
  {/if}
</div>

<style>
  .today-draft-preview {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
  }
  
  .content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
  }
  
  .tasks-list {
    display: flex;
    flex-direction: column;
  }
</style>
