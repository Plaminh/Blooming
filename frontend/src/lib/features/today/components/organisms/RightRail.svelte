<script lang="ts">
  import type { Task, FocusPreset } from '$lib/features/today/types';
  import TodayIcon from '../atoms/TodayIcon.svelte';
  import FocusPresetOption from '../atoms/FocusPresetOption.svelte';
  import NextSessionSummary from '../molecules/NextSessionSummary.svelte';

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
      <img src="/assets/widget/icons/leaf-icon.png" alt="" />
      <h2 id="task-details-heading">TASK DETAILS</h2>
    </header>
    <div class="task-body">
      {#if task}
        <div class="task-summary">
          <TodayIcon name={task.iconRef} scale={1.02} />
          <div>
            <h3>{task.title}</h3>
            <p class="task-time">{task.startTime} – {task.endTime} {task.durationString}</p>
            <p class="description">{task.description ?? 'No description.'}</p>
          </div>
        </div>
        <div class="divider"></div>
        <div class="meta-row">
          <TodayIcon name="category" scale={0.72} />
          <span class="meta-label">Category</span>
          <span class="category-badge">{task.category}</span>
        </div>
        <div class="meta-row notes-row">
          <TodayIcon name="notes" scale={0.72} />
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
      <TodayIcon name="calendar" scale={0.75} />
      <h2 id="next-session-heading">NEXT SESSION</h2>
    </header>
    <NextSessionSummary
      timeText={nextTask ? `Today at ${nextTask.startTime}` : 'No more sessions today'}
      durationText={nextTask ? nextTask.durationString.replace(/[()]/g, '') : ''}
    />
  </section>

  <section class="panel focus-setup" aria-labelledby="focus-heading">
    <header class="panel-strip">
      <img src="/assets/widget/icons/leaf-icon.png" alt="" />
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

  <section class="panel garden" aria-labelledby="garden-heading">
    <header class="panel-strip">
      <img src="/assets/widget/icons/leaf-icon.png" alt="" />
      <h2 id="garden-heading">YOUR GARDEN</h2>
    </header>
    <div class="garden-scene" aria-hidden="true">
      <img class="sky" src="/assets/widget/backgrounds/default-sky.png" alt="" />
      <img class="bushes" src="/assets/widget/backgrounds/background-bushes.png" alt="" />
      <span class="flower f1"></span><span class="flower f2"></span><span class="flower f3"></span>
      <span class="flower f4"></span><span class="flower f5"></span><span class="flower f6"></span>
      <span class="ground"></span>
    </div>
    <footer class="garden-footer">
      <TodayIcon name="sprout" scale={0.72} />
      <strong>UNLOCKED PLANTS</strong>
      <span>1 / 5</span>
    </footer>
  </section>
</div>

<style>
  .right-rail-container {
    display: grid;
    height: 100%;
    grid-template-rows: 240px 94px 220px 1fr;
    gap: 9px;
  }
  .panel {
    min-height: 0;
    overflow: hidden;
    border: 1px solid #20a3be;
    border-radius: 5px;
    background: #fffbf2;
    color: #064b91;
  }
  .panel-strip,
  .plain-header {
    display: flex;
    height: 37px;
    align-items: center;
    gap: 9px;
    padding: 0 12px;
  }
  .panel-strip {
    background: linear-gradient(#3998ad, #24859f);
    color: #f1fbf7;
  }
  .panel-strip img { width: 26px; height: 27px; object-fit: contain; image-rendering: pixelated; }
  h2 {
    flex: 1;
    margin: 0;
    font-family: var(--bloom-body-font);
    font-size: 17px;
    font-weight: 700;
    line-height: 1;
  }
  .task-body { padding: 12px 14px 9px; }
  .task-summary { display: flex; gap: 13px; }
  .task-summary h3 {
    margin: 0;
    color: #063fa0;
    font-family: var(--bloom-body-font);
    font-size: 21px;
    font-weight: 700;
    line-height: 1.1;
  }
  .task-time, .description {
    margin: 3px 0 0;
    color: #0672b0;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    line-height: 1.25;
  }
  .description { margin-top: 6px; }
  .divider { height: 1px; margin: 11px 0 7px; background: #d7d7d1; }
  .meta-row {
    display: grid;
    min-height: 38px;
    grid-template-columns: 34px 90px 1fr;
    align-items: center;
    font-family: var(--bloom-body-font);
    font-size: 14px;
  }
  .meta-label { color: #0873b1; }
  .category-badge {
    justify-self: start;
    padding: 4px 17px;
    border-radius: 5px;
    background: #cceafe;
    color: #0750a8;
  }
  .notes-row { align-items: start; padding-top: 2px; }
  .notes-row .meta-label { padding-top: 4px; }
  .note-copy { padding-top: 3px; color: #074da0; line-height: 1.3; }
  .plain-header { height: 38px; padding-top: 2px; }
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
  .focus-body { padding: 4px 12px 9px; }
  .focus-body > p { margin: 0 0 8px; font-family: var(--bloom-body-font); font-size: 15px; }
  .presets { display: flex; gap: 10px; }
  .start-focus {
    display: flex;
    width: 100%;
    height: 50px;
    align-items: center;
    justify-content: center;
    gap: 18px;
    margin-top: 10px;
    border: 1px solid #177d4d;
    border-radius: 4px;
    background: linear-gradient(#4cad6b, #299655);
    color: white;
    font-family: var(--bloom-body-font);
    font-size: 19px;
    cursor: pointer;
  }
  .start-focus:disabled { opacity: 0.55; cursor: not-allowed; }
  .start-focus:focus-visible { outline: 2px solid #00aeea; outline-offset: 2px; }
  .play { width: 0; height: 0; border-top: 11px solid transparent; border-bottom: 11px solid transparent; border-left: 17px solid white; }
  .garden { display: grid; grid-template-rows: 37px 1fr 55px; }
  .garden-scene { position: relative; min-height: 0; overflow: hidden; border-bottom: 5px solid #bfb8a9; background: #6fcdf5; }
  .garden-scene img { position: absolute; max-width: none; height: auto; image-rendering: pixelated; }
  .sky { left: 0; bottom: -10px; width: 100%; }
  .bushes { left: -50%; bottom: -69px; width: 200%; }
  .ground { position: absolute; inset: auto 0 0; height: 10px; background: #f5d18a; border-top: 3px solid #196d54; }
  .flower { position: absolute; bottom: 12px; width: 6px; height: 22px; background: #2a9561; }
  .flower::before { content: ''; position: absolute; top: 0; left: -5px; width: 16px; height: 9px; background: #ff77a8; box-shadow: inset 5px 0 #ffd9a2, inset -5px 0 #ff8db8; }
  .f1 { left: 16%; }.f2 { left: 31%; }.f3 { left: 47%; }.f4 { left: 62%; }.f5 { left: 78%; }.f6 { left: 91%; }
  .garden-footer { display: flex; align-items: center; gap: 7px; padding: 0 12px; font-family: var(--bloom-body-font); font-size: 15px; color: #064798; }
  .garden-footer span:last-child { margin-left: auto; }
  .empty-state { padding: 20px; font-family: var(--bloom-body-font); }
</style>
