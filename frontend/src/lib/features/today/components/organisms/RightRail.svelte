<script lang="ts">
  import type { Task, FocusPreset } from '$lib/features/today/types';
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import FocusPresetOption from '../atoms/FocusPresetOption.svelte';
  import NextSessionSummary from '../molecules/NextSessionSummary.svelte';
  import GardenPanel from '$lib/shared/components/organisms/GardenPanel.svelte';

  let { task, nextTask, selectedFocusPreset, onPresetSelect, onStartFocus }: {
    task: Task | undefined;
    nextTask: Task | undefined;
    selectedFocusPreset: FocusPreset;
    onPresetSelect: (preset: FocusPreset) => void;
    onStartFocus: () => void;
  } = $props();

  const presets = [
    { id: '25/5', label: '25/5', focus: '25 min focus', break: '5 min break' },
    { id: '50/10', label: '50/10', focus: '50 min focus', break: '10 min break' },
    { id: 'Custom', label: 'CUSTOM', focus: 'Set your own', break: 'timer' }
  ] as const;
</script>

<div class="right-rail-container">
  <section class="panel task-details" aria-labelledby="task-details-heading">
    <header class="panel-strip">
      <h2 id="task-details-heading">TASK DETAILS</h2>
    </header>
    <div class="task-body">
      {#if task}
        <div class="task-summary">
          <span class="detail-icon"><AppIcon name={task.iconRef} size="detail" /></span>
          <div>
            <h3>{task.title}</h3>
            <p class="task-time">{task.startTime} – {task.endTime} {task.durationString}</p>
            <p class="description">{task.description ?? 'No description.'}</p>
          </div>
        </div>
        <div class="divider"></div>
        <div class="meta-row">
          <AppIcon name="category" scale={0.72} />
          <span class="meta-label">Category</span>
          <span class="category-badge">{task.category}</span>
        </div>
        <div class="meta-row notes-row">
          <AppIcon name="notes" scale={0.72} />
          <span class="meta-label">Notes</span>
          <span class="note-copy">{task.notes ?? 'No additional notes.'}</span>
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
      timeText={nextTask ? `Today at ${nextTask.startTime}` : 'No more sessions today'}
      durationText={nextTask ? nextTask.durationString.replace(/[()]/g, '') : ''}
    />
  </section>

  <section class="panel focus-setup" aria-labelledby="focus-heading">
    <header class="panel-strip">
      <h2 id="focus-heading">FOCUS SETUP</h2>
      <span class="help" aria-label="Focus setup help">?</span>
    </header>
    <div class="focus-body">
      <p>Focus for this task</p>
      <div class="presets">
        {#each presets as preset}
          <FocusPresetOption
            preset={preset.id}
            label={preset.label}
            focusTime={preset.focus}
            breakTime={preset.break}
            selected={selectedFocusPreset === preset.id}
            onSelect={onPresetSelect}
          />
        {/each}
      </div>
      <button class="start-focus" onclick={onStartFocus} disabled={!task}>
        <span class="play" aria-hidden="true"></span>
        <span>START FOCUS</span>
      </button>
    </div>
  </section>

  <GardenPanel />
</div>

<style>
  .right-rail-container {
    display: grid;
    height: 100%;
    grid-template-rows: 210px 82px 190px minmax(0, 1fr);
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
  .task-details { display: flex; flex-direction: column; }
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
  .task-body { min-height: 0; flex: 1; padding: 8px 10px 6px; overflow-y: auto; }
  .task-summary { display: flex; gap: 10px; }
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
  .task-time, .description {
    margin: 3px 0 0;
    color: #0672b0;
    font-family: var(--bloom-body-font);
    font-size: 13px;
    line-height: 1.25;
  }
  .description { margin-top: 4px; }
  .divider { height: 1px; margin: 7px 0 4px; background: #d7d7d1; }
  .meta-row {
    display: grid;
    min-height: 31px;
    grid-template-columns: 28px 74px 1fr;
    align-items: center;
    font-family: var(--bloom-body-font);
    font-size: 12px;
  }
  .meta-label { color: #0873b1; }
  .category-badge {
    justify-self: start;
    padding: 3px 12px;
    border-radius: 5px;
    background: #cceafe;
    color: #0750a8;
  }
  .notes-row { align-items: start; padding-top: 2px; }
  .notes-row .meta-label { padding-top: 4px; }
  .note-copy { padding-top: 3px; color: #074da0; line-height: 1.3; }
  .plain-header { height: 32px; padding-top: 1px; }
  .plain-header h2 { color: #06447f; }
  .help {
    display: grid;
    width: 23px;
    height: 23px;
    place-items: center;
    border: 2px solid white;
    border-radius: 50%;
    font-size: 15px;
    font-weight: 800;
    line-height: 1;
  }
  .focus-body { padding: 3px 10px 7px; }
  .focus-body > p { margin: 0 0 5px; font-family: var(--bloom-body-font); font-size: 13px; }
  .presets { display: flex; gap: 8px; }
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
  .start-focus:disabled { opacity: 0.55; cursor: not-allowed; }
  .start-focus:focus-visible { outline: 2px solid #00aeea; outline-offset: 2px; }
  .play { width: 0; height: 0; border-top: 8px solid transparent; border-bottom: 8px solid transparent; border-left: 13px solid white; }

  .empty-state { padding: 20px; font-family: var(--bloom-body-font); }
</style>
