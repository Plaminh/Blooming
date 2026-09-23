<script lang="ts">
  import { mrBloomStore, type TodayDraft } from '../../stores/mrBloomStore';
  import DraftTaskSummary from '../molecules/DraftTaskSummary.svelte';
  import DraftReviewActionBar from './DraftReviewActionBar.svelte';
  import DraftReviewHeader from './DraftReviewHeader.svelte';
  import DraftAddButton from '../molecules/DraftAddButton.svelte';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let draft = $derived($mrBloomStore.activeDraft as TodayDraft);
  let addingTask = $state(false);
  let newTitle = $state('');
  let newDuration = $state(25);
  function addTask() {
    if (!newTitle.trim()) return;
    mrBloomStore.addTask(newTitle, newDuration);
    newTitle = '';
    newDuration = 25;
    addingTask = false;
  }
  let availabilityText = $derived(
    draft?.windows.map(window => `${window.start}–${window.end}`).join(', ') || 'No availability set'
  );
  let budgetAssumption = $derived($mrBloomStore.assumptions.find(a => a.text.startsWith('Normalized budget:')));
  let timeBudgetMinutes = $derived(budgetAssumption ? Number.parseInt(budgetAssumption.text.match(/\d+/)?.[0] || '0', 10) : null);
  let otherAssumptions = $derived($mrBloomStore.assumptions.filter(a => a !== budgetAssumption));
  let hasTasks = $derived((draft?.tasks?.length || 0) > 0);
</script>

<div class="today-draft-preview">
  {#if draft?.type === 'today'}
    <DraftReviewHeader
      title="TODAY DRAFT"
      subtitle="Review the extracted tasks before generating your timeline."
    />

    <div class="content">
      <div class="availability-bar">
        <span class="availability-icon"><AppIcon name="calendar" size="detail" /></span>
        <span>Available · {availabilityText}</span>
      </div>

      {#if timeBudgetMinutes !== null}
        <div class="budget-bar">
          <span class="availability-icon"><AppIcon name="calendar" size="detail" /></span>
          <span>Time budget · {timeBudgetMinutes} minutes</span>
        </div>
      {/if}

      <div class="tasks-list">
        {#each draft.tasks as task (task.id)}
          <DraftTaskSummary {task} />
        {/each}
        {#if !hasTasks}
          <div class="empty-tasks-prompt">
            Please add tasks to schedule within your available time.
          </div>
        {/if}
      </div>

      {#if otherAssumptions.length}
        <section class="assumptions" aria-label="Planning assumptions">
          <strong>Assumptions</strong>
          <ul>
            {#each otherAssumptions as assumption (assumption.id)}
              <li>{assumption.text}</li>
            {/each}
          </ul>
        </section>
      {/if}

      {#if addingTask}
        <form class="add-task-form" onsubmit={(event) => { event.preventDefault(); addTask(); }}>
          <input aria-label="New task title" placeholder="Task name" bind:value={newTitle} maxlength="200" required />
          <input aria-label="New task duration in minutes" type="number" min="5" max="480" step="5" bind:value={newDuration} required />
          <button type="submit">ADD</button>
          <button type="button" onclick={() => addingTask = false}>CANCEL</button>
        </form>
      {:else}
        <DraftAddButton label="ADD TASK" variant="task" onclick={() => addingTask = true} />
      {/if}
      <div class="content-divider" aria-hidden="true"></div>
    </div>

    <DraftReviewActionBar
      primaryLabel="GENERATE TIMELINE"
      iconSize="control"
      onPrimary={() => mrBloomStore.generateTimeline()}
      disabled={!hasTasks || $mrBloomStore.isDraftMutationPending || $mrBloomStore.isPreviewPending}
    />
  {/if}
</div>

<style>
  .today-draft-preview {
    display: flex;
    width: 100%;
    height: 100%;
    min-width: 0;
    min-height: 0;
    flex-direction: column;
  }

  .content {
    display: flex;
    min-height: 0;
    flex: 1;
    flex-direction: column;
    gap: 10px;
    padding: 10px 12px 0;
    overflow-y: auto;
  }

  .availability-bar {
    display: flex;
    min-height: 50px;
    flex: 0 0 50px;
    align-items: center;
    gap: 12px;
    padding: 6px 12px;
    border: 2px solid #70c7ed;
    border-radius: 5px;
    background: var(--bloom-task-active-bg);
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 16px;
  }

  .availability-icon {
    display: grid;
    width: var(--bloom-icon-detail);
    height: var(--bloom-icon-detail);
    flex: 0 0 var(--bloom-icon-detail);
    place-items: center;
    color: #0b506e;
  }

  .tasks-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .content-divider {
    width: 100%;
    margin-top: -6px;
    border-top: 2px solid #c8cfca;
  }

  .assumptions {
    padding: 9px 12px;
    border: 1px solid #e1c56d;
    border-radius: 5px;
    background: #fff9df;
    color: #684f0b;
    font-family: var(--bloom-body-font);
    font-size: 14px;
  }

  .assumptions ul { margin: 5px 0 0; padding-left: 20px; }
  .add-task-form { display: flex; flex-wrap: wrap; gap: 6px; }
  .add-task-form input { min-width: 0; padding: 6px; }
  .add-task-form input:first-child { flex: 1; }
  .add-task-form input[type='number'] { width: 72px; }
</style>
