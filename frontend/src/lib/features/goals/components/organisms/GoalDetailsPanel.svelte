<script lang="ts">
  import type { Goal } from '../../models';
  import TargetDateLabel from '../atoms/TargetDateLabel.svelte';
  import RoadmapTimeline from './RoadmapTimeline.svelte';
  import AppIcon, { type IconName } from '$lib/shared/components/atoms/AppIcon.svelte';
  import GoalsPanelHeader from '../atoms/GoalsPanelHeader.svelte';
  import TextInput from '$lib/shared/components/atoms/TextInput.svelte';
  import { goalsStore } from '../../stores/goalsStore';

  let { goal, onUpdateMilestone }: { 
    goal: Goal | null, 
    onUpdateMilestone?: (milestoneId: string, updates: any) => void 
  } = $props();

  let isEditing = $state(false);
  let editTitle = $state("");
  let editDescription = $state("");
  let saving = $state(false);
  let errorMsg = $state("");

  function startEdit() {
    if (goal) {
      editTitle = goal.title;
      editDescription = goal.description || "";
      errorMsg = "";
      isEditing = true;
    }
  }

  async function saveEdit() {
    if (!goal || saving || !editTitle.trim()) return;
    saving = true;
    errorMsg = "";
    try {
      await goalsStore.updateGoal(goal.id, { title: editTitle, description: editDescription });
      isEditing = false;
    } catch (e) {
      errorMsg = e instanceof Error ? e.message : "Failed to save goal";
    } finally {
      saving = false;
    }
  }

  function cancelEdit() {
    isEditing = false;
  }
</script>

<section class="panel goal-details">
  <GoalsPanelHeader title="GOAL DETAILS" id="goal-details-heading" />
  
  <div class="panel-body">
    {#if goal}
      <div class="goal-summary">
        {#if goal.iconRef !== 'leaf' && goal.iconRef !== 'sprout'}
          <div class="summary-icon">
            <AppIcon name={goal.iconRef as IconName} size="goal-detail" />
          </div>
        {/if}
        <div class="summary-text">
          {#if isEditing}
            <div class="edit-form">
              {#if errorMsg}
                <div class="error-msg">{errorMsg}</div>
              {/if}
              <TextInput bind:value={editTitle} placeholder="Goal Title" disabled={saving} />
              <textarea class="edit-desc" bind:value={editDescription} placeholder="Goal Description" disabled={saving}></textarea>
              <div class="edit-actions">
                <button class="btn-cancel" onclick={cancelEdit} disabled={saving}>Cancel</button>
                <button class="btn-save" onclick={saveEdit} disabled={saving || !editTitle.trim()}>Save</button>
              </div>
            </div>
          {:else}
            <div class="title-row">
              <h3>{goal.title}</h3>
              <button class="invisible-button edit-btn" onclick={startEdit} aria-label="Edit Goal">
                <AppIcon name="pencil" scale={0.9} />
              </button>
            </div>
            <p>{goal.description}</p>
          {/if}
        </div>
        <div class="target-date-box">
          <span class="box-label">Target date</span>
          <TargetDateLabel date={goal.target_date} />
        </div>
      </div>
      
      <h3 class="roadmap-heading">ROADMAP</h3>
      <RoadmapTimeline milestones={goal.milestones} {onUpdateMilestone} />
    {:else}
      <div class="empty-state">
        <p>No goal selected.</p>
      </div>
    {/if}
  </div>
</section>

<style>
  .panel {
    background: rgba(255, 253, 247, 0.78);
    border: 1px solid #aab6aa;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }
  .panel-body {
    padding: 14px 12px 12px 14px;
    flex: 1;
    overflow-y: auto;
  }
  .goal-summary {
    display: flex;
    min-height: 64px;
    gap: 12px;
    margin-bottom: 12px;
    align-items: flex-start;
  }
  .summary-icon {
    color: #0872ae;
    width: var(--bloom-icon-goal-detail);
    height: var(--bloom-icon-goal-detail);
    flex: 0 0 var(--bloom-icon-goal-detail);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 4px;
  }
  .summary-text {
    flex: 1;
    min-width: 0;
  }
  .title-row {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 4px;
  }
  .title-row h3 {
    margin: 0;
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.06em;
  }
  .edit-btn {
    opacity: 0;
    transition: opacity 0.2s;
    color: #1479ab;
    margin-top: 2px;
  }
  .title-row:hover .edit-btn {
    opacity: 1;
  }
  .invisible-button {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
  }
  .summary-text p {
    margin: 0;
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    line-height: 1.3;
  }
  .edit-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .edit-desc {
    width: 100%;
    height: 60px;
    resize: none;
    border: 1px solid #dcd7ca;
    border-radius: 4px;
    padding: 6px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
  }
  .edit-actions {
    display: flex;
    justify-content: flex-end;
    gap: 6px;
  }
  .btn-save, .btn-cancel {
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
  }
  .btn-save {
    background: #064b91;
    color: white;
    border: none;
  }
  .btn-save:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  .btn-cancel {
    background: white;
    border: 1px solid #dcd7ca;
    color: #333;
  }
  .target-date-box {
    border: 1px solid #dcd7ca;
    background: #fffdf8;
    width: 116px;
    height: 62px;
    flex: 0 0 116px;
    padding: 6px 7px;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    box-sizing: border-box;
  }
  .box-label {
    color: #0c61a1;
    font-family: var(--bloom-body-font);
    font-size: 12px;
  }
  .roadmap-heading {
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 23px;
    font-weight: 800;
    letter-spacing: -0.055em;
    margin: 0 0 8px 0;
  }
  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 16px;
  }
  .error-msg {
    color: #d32f2f;
    font-size: 12px;
    font-family: var(--bloom-body-font);
    background: #ffebee;
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid #ffcdd2;
  }
</style>
