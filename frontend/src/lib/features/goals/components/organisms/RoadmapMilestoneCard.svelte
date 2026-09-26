<script lang="ts">
  import type { Milestone } from '../../models';
  import GoalStatusBadge from '../atoms/GoalStatusBadge.svelte';
  import TargetDateLabel from '../atoms/TargetDateLabel.svelte';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import TextInput from '$lib/shared/components/atoms/TextInput.svelte';

  let { milestone, onUpdateMilestone }: { 
    milestone: Milestone, 
    onUpdateMilestone?: (id: string, updates: any) => void 
  } = $props();

  let isEditing = $state(false);
  let editTitle = $state("");
  let editOutcome = $state("");
  let editDate = $state("");
  let saving = $state(false);
  let errorMsg = $state("");

  function startEdit() {
    editTitle = milestone.title;
    editOutcome = milestone.expected_outcome || "";
    editDate = milestone.target_date || "";
    errorMsg = "";
    isEditing = true;
  }

  async function saveEdit() {
    if (!editTitle.trim() || saving) return;
    saving = true;
    errorMsg = "";
    try {
        if (onUpdateMilestone) {
            await onUpdateMilestone(milestone.id, { 
                title: editTitle, 
                expected_outcome: editOutcome,
                target_date: editDate || undefined
            });
        }
        isEditing = false;
    } catch (e) {
        errorMsg = e instanceof Error ? e.message : "Failed to save milestone";
    } finally {
        saving = false;
    }
  }

  function cancelEdit() {
    isEditing = false;
  }

  function handleMarkComplete() {
    if (onUpdateMilestone) {
        onUpdateMilestone(milestone.id, { status: 'COMPLETED' });
    }
  }
</script>

<div class="milestone-card" class:completed={milestone.status === 'COMPLETED'}>
  {#if isEditing}
    <div class="edit-form">
      {#if errorMsg}
        <div class="error-msg">{errorMsg}</div>
      {/if}
      <TextInput bind:value={editTitle} placeholder="Milestone Title" disabled={saving} />
      <textarea class="edit-desc" bind:value={editOutcome} placeholder="Expected Outcome" disabled={saving}></textarea>
      <input type="date" class="edit-date" bind:value={editDate} disabled={saving} />
      <div class="edit-actions">
        <button class="btn-cancel" onclick={cancelEdit} disabled={saving}>Cancel</button>
        <button class="btn-save" onclick={saveEdit} disabled={saving || !editTitle.trim()}>Save</button>
      </div>
    </div>
  {:else}
    <div class="title-row">
      <h4>{milestone.title}</h4>
      <button class="invisible-button edit-btn" onclick={startEdit} aria-label="Edit Milestone">
        <AppIcon name="pencil" scale={0.8} />
      </button>
    </div>
    <p>{milestone.expected_outcome || ""}</p>
    <div class="meta-row">
      <div class="date-container">
        <TargetDateLabel date={milestone.target_date || (milestone.due_at ? new Date(milestone.due_at).toLocaleDateString() : '')} />
      </div>
      <div class="status-actions">
        {#if milestone.status !== 'COMPLETED'}
          <button class="btn-mark-complete" onclick={handleMarkComplete}>MARK COMPLETE</button>
        {/if}
        <GoalStatusBadge status={milestone.status} />
      </div>
    </div>
  {/if}
</div>

<style>
  .milestone-card {
    background: #fffdf8;
    border: 1px solid #d9d5c8;
    border-radius: 6px;
    min-height: 108px;
    padding: 8px 12px;
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  .milestone-card.completed { background: #f2faef; border-color: #bfd8c2; }
  .title-row {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    margin-bottom: 3px;
  }
  h4 {
    margin: 0;
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.055em;
    line-height: 1.2;
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
  p {
    margin: 0 0 8px 0;
    color: #0a65a2;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    line-height: 1.25;
  }
  .meta-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
  }
  .status-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .btn-mark-complete {
    background: #eef8f6;
    border: 1px solid #bfd8c2;
    border-radius: 4px;
    color: #247b4c;
    font-family: var(--bloom-display-font);
    font-size: 11px;
    font-weight: 800;
    padding: 4px 8px;
    cursor: pointer;
  }
  .btn-mark-complete:hover {
    background: #e1f1ec;
  }
  .invisible-button {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
  }
  .edit-form {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .edit-desc {
    width: 100%;
    height: 40px;
    resize: none;
    border: 1px solid #dcd7ca;
    border-radius: 4px;
    padding: 6px;
    font-family: var(--bloom-body-font);
    font-size: 12px;
  }
  .edit-date {
    width: 130px;
    border: 1px solid #dcd7ca;
    border-radius: 4px;
    padding: 4px 6px;
    font-family: var(--bloom-body-font);
    font-size: 12px;
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
