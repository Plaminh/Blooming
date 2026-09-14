<script lang="ts">
  import { mrBloomStore, type RoadmapDraft } from '../../stores/mrBloomStore';
  import DraftReviewHeader from './DraftReviewHeader.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import DateNavigator from '../molecules/DateNavigator.svelte';
  
  let draft = $derived($mrBloomStore.activeDraft as RoadmapDraft);
  
  function handleAccept() {
    mrBloomStore.acceptDraft("Great! I've saved that roadmap to your Goals.");
  }
</script>

<div class="plan-draft-preview">
  {#if draft}
    <DraftReviewHeader 
      type="ROADMAP" 
      title={draft.goalTitle} 
      subtitle={draft.goalDescription} 
    />
    
    <div class="content">
      <div class="target-container">
        <DateNavigator bind:date={draft.targetDate} />
      </div>
      
      <div class="milestones">
        {#each draft.milestones as milestone, i}
          <div class="milestone-card">
            <div class="milestone-number">M{i+1}</div>
            <div class="milestone-info">
              <div class="milestone-title">{milestone.title}</div>
              <div class="milestone-date">By {milestone.targetDate}</div>
            </div>
          </div>
        {/each}
      </div>
    </div>
    
    <DraftReviewActionBar 
      primaryLabel="Save to Goals" 
      onPrimary={handleAccept} 
    />
  {/if}
</div>

<style>
  .plan-draft-preview {
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
  
  .target-container {
    margin-bottom: 24px;
  }
  
  .milestones {
    display: flex;
    flex-direction: column;
    gap: 16px;
    position: relative;
    padding-left: 24px;
  }
  
  .milestones::before {
    content: '';
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #cfc9b9;
  }
  
  .milestone-card {
    background: #ffffff;
    border: 1px solid #cfc9b9;
    border-radius: 6px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 16px;
    position: relative;
  }
  
  .milestone-card::before {
    content: '';
    position: absolute;
    left: -20px;
    top: 50%;
    transform: translateY(-50%);
    width: 12px;
    height: 2px;
    background: #cfc9b9;
  }
  
  .milestone-card::after {
    content: '';
    position: absolute;
    left: -24px;
    top: 50%;
    transform: translateY(-50%);
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #a9e0f5;
    border: 2px solid #ffffff;
    box-shadow: 0 0 0 1px #cfc9b9;
  }
  
  .milestone-number {
    font-family: var(--bloom-header-font, 'Pixelify Sans', sans-serif);
    font-size: 16px;
    color: #92b9d4;
  }
  
  .milestone-info {
    flex: 1;
  }
  
  .milestone-title {
    font-family: var(--bloom-body-font);
    font-weight: 700;
    font-size: 15px;
    color: #064798;
    margin-bottom: 4px;
  }
  
  .milestone-date {
    font-family: var(--bloom-body-font);
    font-size: 12px;
    color: #92b9d4;
  }
</style>
