<script lang="ts">
  import type { Category, TodayTaskEdit } from "$lib/api/types";
  import type { Task, FocusPreset } from "$lib/features/today/types";
  import AppIcon from "$lib/shared/components/atoms/AppIcon.svelte";
  import FocusPresetOption from "../atoms/FocusPresetOption.svelte";
  import NextSessionSummary from "../molecules/NextSessionSummary.svelte";
  import CustomFocusDialog from './CustomFocusDialog.svelte';
  let {
    task,
    nextTask,
    selectedFocusPreset,
    customFocusMinutes,
    customBreakMinutes,
    onPresetSelect,
    onCustomSaved,
    onStartFocus,
    onSaveTask,
    focusDisabled = false,
  }: {
    task: Task | undefined;
    nextTask: Task | undefined;
    selectedFocusPreset: FocusPreset;
    customFocusMinutes: number;
    customBreakMinutes: number;
    onPresetSelect: (preset: FocusPreset) => void;
    onCustomSaved: (focusMinutes: number, breakMinutes: number) => void;
    onStartFocus: () => void;
    onSaveTask: (id: string, updates: TodayTaskEdit) => Promise<void>;
    focusDisabled?: boolean;
  } = $props();

  const presets = [
    { id: "25/5", label: "25/5", focus: "25 min focus", break: "5 min break" },
    {
      id: "50/10",
      label: "50/10",
      focus: "50 min focus",
      break: "10 min break",
    },
    { id: "Custom", label: "CUSTOM", focus: "Set your own", break: "timer" },
  ] as const;

  let isEditing = $state(false);
  let editCategory = $state<Category>(null);
  let editTitle = $state("");
  let editDuration = $state(25);
  let editTaskId = $state<string | null>(null);
  let saveError = $state<string | null>(null);
  let editDescription = $state<string>("");
  let isSaving = $state(false);
  let customDialogOpen = $state(false);

  function selectFocusPreset(preset: FocusPreset) {
    if (preset === 'Custom') customDialogOpen = true;
    else onPresetSelect(preset);
  }

  export function startEditing() {
    if (!task?.task_id || isSaving || isEditing) return;
    editTaskId = task.task_id;
    editTitle = task.title;
    editDuration = task.estimatedDurationMinutes ?? 25;
    editCategory = task.category;
    editDescription = task.description ?? "";
    saveError = null;
    isEditing = true;
  }

  async function handleSave() {
    if (!editTaskId || isSaving) return;
    if (
      !editTitle.trim() ||
      editTitle.length > 200 ||
      !Number.isInteger(editDuration) ||
      editDuration < 1 ||
      editDuration > 10080
    ) {
      saveError = "Enter a title and a duration between 1 and 10080 minutes.";
      return;
    }
    isSaving = true;
    saveError = null;
    try {
      await onSaveTask(editTaskId, {
        title: editTitle.trim(),
        estimated_duration_minutes: editDuration,
        category: editCategory,
        description: editDescription || null,
      });
      isEditing = false;
    } catch (error: unknown) {
      saveError =
        error instanceof Error
          ? error.message
          : "Failed to save. Your draft is preserved.";
    } finally {
      isSaving = false;
    }
  }
</script>

<div class="right-rail-container">
  <section class="panel task-details" aria-labelledby="task-details-heading">
    <header class="panel-strip">
      <h2 id="task-details-heading">TASK DETAILS</h2>
      {#if task}
        {#if isEditing}
          <button class="edit-toggle" onclick={handleSave} disabled={isSaving}
            >Save</button
          >
          <button
            class="edit-toggle"
            onclick={() => (isEditing = false)}
            disabled={isSaving}>Cancel</button
          >
        {:else}
          <button
            class="edit-toggle"
            onclick={startEditing}
            disabled={!task.task_id}
            aria-label="Edit task"
          >
            <AppIcon name="pencil" scale={0.8} />
          </button>
        {/if}
      {/if}
    </header>
    <div class="task-body">
      {#if saveError}<p role="alert">{saveError}</p>{/if}
      {#if isEditing}
        <label>Title <input bind:value={editTitle} maxlength="200" /></label>
        <label
          >Duration (minutes) <input
            type="number"
            bind:value={editDuration}
            min="1"
            max="10080"
          /></label
        >
      {/if}
      {#if task}
        <div class="task-summary">
          <span class="detail-icon"
            ><AppIcon name={task.iconRef} size="detail" /></span
          >
          <div>
            <h3>{task.title}</h3>
            <p class="task-time">
              {task.startTime} – {task.endTime}
              {task.durationString}
            </p>
            <p class="description">{task.description ?? "No description."}</p>
          </div>
        </div>
        <div class="divider"></div>
        <div class="meta-row">
          <AppIcon name="category" scale={0.72} />
          <span class="meta-label">Category</span>
          {#if isEditing}
            <select
              aria-label="Category"
              bind:value={editCategory}
              class="category-select"
            >
              <option value={null}>Uncategorized</option>
              <option value="Learning">Learning</option>
              <option value="Work">Work</option>
              <option value="Personal">Personal</option>
            </select>
          {:else}
            <span class="category-badge"
              >{task.category ?? "Uncategorized"}</span
            >
          {/if}
        </div>
        <div class="meta-row notes-row">
          <AppIcon name="notes" scale={0.72} />
          <span class="meta-label">Notes</span>
          {#if isEditing}
            <textarea
              aria-label="Notes"
              bind:value={editDescription}
              class="notes-textarea"
              placeholder="Add notes..."></textarea>
          {:else}
            <span class="note-copy">{task.notes ?? "No additional notes."}</span
            >
          {/if}
        </div>
      {:else}
        <p class="empty-state">No task selected.</p>
      {/if}
    </div>
  </section>

  <section class="panel next-session" aria-labelledby="next-session-heading">
    <header class="plain-header">
      <AppIcon name="calendar" scale={0.75} />
      <h2 id="next-session-heading">NEXT SESSION</h2>
    </header>
    <NextSessionSummary
      timeText={nextTask
        ? `Today at ${nextTask.startTime}`
        : "No more sessions today"}
      durationText={nextTask
        ? nextTask.durationString.replace(/[()]/g, "")
        : ""}
    />
  </section>

  <section class="panel focus-setup" aria-labelledby="focus-heading">
    <header class="panel-strip">
      <h2 id="focus-heading">FOCUS SETUP</h2>
    </header>
    <div class="focus-body">
      <p>Focus for this task</p>
      <div class="presets">
        {#each presets as preset}
          <FocusPresetOption
            preset={preset.id}
            label={preset.label}
            focusTime={preset.id === 'Custom' && selectedFocusPreset === 'Custom' ? `${customFocusMinutes} min focus` : preset.focus}
            breakTime={preset.id === 'Custom' && selectedFocusPreset === 'Custom' ? `${customBreakMinutes} min break` : preset.break}
            selected={selectedFocusPreset === preset.id}
            onSelect={selectFocusPreset}
          />
        {/each}
      </div>
      <button
        class="start-focus"
        onclick={onStartFocus}
        disabled={!task?.task_id || focusDisabled}
      >
        <span class="play" aria-hidden="true"></span>
        <span>START FOCUS</span>
      </button>
    </div>
  </section>
</div>

<CustomFocusDialog
  open={customDialogOpen}
  onClose={() => customDialogOpen = false}
  onSave={(focusMinutes, breakMinutes) => onCustomSaved(focusMinutes, breakMinutes)}
/>

<style>
  .right-rail-container {
    display: grid;
    height: 100%;
    grid-template-rows: 210px 82px 190px;
    gap: 8px;
  }
  .panel {
    min-height: 0;
    overflow: hidden;
    border: 1px solid #20a3be;
    border-radius: 5px;
    background: #fffbf2;
    color: #064b91;
  }
  .task-details {
    display: flex;
    flex-direction: column;
  }
  .panel-strip,
  .plain-header {
    display: flex;
    height: 32px;
    align-items: center;
    gap: 7px;
    padding: 0 10px;
  }
  .panel-strip {
    background: var(--bloom-titlebar-bg);
    color: #f1fbf7;
  }
  h2 {
    flex: 1;
    margin: 0;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    font-weight: 700;
    line-height: 1;
  }
  .task-body {
    min-height: 0;
    flex: 1;
    padding: 8px 10px 6px;
    overflow-y: auto;
  }
  .task-summary {
    display: flex;
    gap: 10px;
  }
  .detail-icon {
    display: grid;
    width: var(--bloom-icon-detail-slot);
    height: var(--bloom-icon-detail-slot);
    flex: 0 0 var(--bloom-icon-detail-slot);
    place-items: center;
  }
  .task-summary h3 {
    margin: 0;
    color: #063fa0;
    font-family: var(--bloom-body-font);
    font-size: 18px;
    font-weight: 700;
    line-height: 1.1;
  }
  .task-time,
  .description {
    margin: 3px 0 0;
    color: #0672b0;
    font-family: var(--bloom-body-font);
    font-size: 13px;
    line-height: 1.25;
  }
  .description {
    margin-top: 4px;
  }
  .divider {
    height: 1px;
    margin: 7px 0 4px;
    background: #d7d7d1;
  }
  .meta-row {
    display: grid;
    min-height: 31px;
    grid-template-columns: 28px 74px 1fr;
    align-items: center;
    font-family: var(--bloom-body-font);
    font-size: 12px;
  }
  .meta-label {
    color: #0873b1;
  }
  .category-badge {
    justify-self: start;
    padding: 3px 12px;
    border-radius: 5px;
    background: #cceafe;
    color: #0750a8;
  }
  .notes-row {
    align-items: start;
    padding-top: 2px;
  }
  .notes-row .meta-label {
    padding-top: 4px;
  }
  .note-copy {
    padding-top: 3px;
    color: #074da0;
    line-height: 1.3;
  }
  .plain-header {
    height: 32px;
    padding-top: 1px;
  }
  .plain-header h2 {
    color: #06447f;
  }

  .edit-toggle {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 4px;
    color: white;
    cursor: pointer;
    font-size: 12px;
    padding: 2px 8px;
    margin-left: 5px;
  }
  .edit-toggle:hover {
    background: rgba(255, 255, 255, 0.2);
  }
  .edit-toggle:disabled {
    opacity: 0.5;
  }

  .category-select {
    justify-self: start;
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid #cceafe;
    background: #fff;
    color: #0750a8;
  }
  .notes-textarea {
    width: 100%;
    min-height: 60px;
    margin-top: 3px;
    padding: 4px 6px;
    border: 1px solid #cceafe;
    border-radius: 4px;
    background: #fff;
    color: #074da0;
    font-family: inherit;
    resize: vertical;
  }
  .focus-body {
    padding: 3px 10px 7px;
  }
  .focus-body > p {
    margin: 0 0 5px;
    font-family: var(--bloom-body-font);
    font-size: 13px;
  }
  .presets {
    display: flex;
    gap: 8px;
  }
  .start-focus {
    display: flex;
    width: 100%;
    height: 42px;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-top: 7px;
    border: 1px solid #177d4d;
    border-radius: 4px;
    background: var(--bloom-action-primary-bg);
    color: white;
    font-family: var(--bloom-body-font);
    font-size: 16px;
    cursor: pointer;
  }
  .start-focus:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }
  .start-focus:focus-visible {
    outline: 2px solid #00aeea;
    outline-offset: 2px;
  }
  .play {
    width: 0;
    height: 0;
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
    border-left: 13px solid white;
  }

  .empty-state {
    padding: 20px;
    font-family: var(--bloom-body-font);
  }
</style>
