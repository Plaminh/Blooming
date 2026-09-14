<script lang="ts">
  import DesktopTitleBar from '$lib/shared/components/organisms/DesktopTitleBar.svelte';
  import AppSidebar from '$lib/shared/components/organisms/AppSidebar.svelte';
  import BottomActions from '$lib/features/today/components/organisms/BottomActions.svelte';
  import RightRail from '$lib/features/today/components/organisms/RightRail.svelte';
  import TodayTimeline from '$lib/features/today/components/organisms/TodayTimeline.svelte';
  import type { FocusPreset, Task } from '$lib/features/today/types';

  const referenceTasks: Task[] = [
    {
      id: '1',
      title: 'Study databases',
      startTime: '09:00',
      endTime: '10:00',
      durationString: '(1 hour)',
      status: 'in-progress',
      category: 'Learning',
      description: 'Read chapters 3–4 and take notes.',
      notes: 'Focus on query design and indexing.',
      iconRef: 'book'
    },
    {
      id: '2', title: 'Break', startTime: '10:00', endTime: '10:30', durationString: '(30 min)',
      status: 'completed', category: 'Personal', description: 'Take a short break.', iconRef: 'break'
    },
    {
      id: '3', title: 'Finish proposal', startTime: '11:00', endTime: '12:00', durationString: '(1 hour)',
      status: 'upcoming', category: 'Work', description: 'Complete the proposal draft.', iconRef: 'document'
    },
    {
      id: '4', title: 'Go for a walk', startTime: '13:00', endTime: '14:00', durationString: '(1 hour)',
      status: 'upcoming', category: 'Personal', description: 'Get outside for some fresh air.', iconRef: 'shoe'
    }
  ];

  let currentDate = $state(new Date(2024, 3, 23));
  let tasks = $state<Task[]>([...referenceTasks]);
  let selectedTaskId = $state('1');
  let selectedFocusPreset = $state<FocusPreset>('25/5');

  const selectedTask = $derived(tasks.find((task) => task.id === selectedTaskId));
  const nextTask = $derived(tasks.find((task) => task.status === 'upcoming'));

  function isReferenceDate(date: Date) {
    return date.getFullYear() === 2024 && date.getMonth() === 3 && date.getDate() === 23;
  }

  function updateSchedule() {
    tasks = isReferenceDate(currentDate) ? [...referenceTasks] : [];
    selectedTaskId = tasks[0]?.id ?? '';
  }

  function handleDateChange(offset: number) {
    if (offset === 0) {
      currentDate = new Date();
    } else {
      const nextDate = new Date(currentDate);
      nextDate.setDate(nextDate.getDate() + offset);
      currentDate = nextDate;
    }
    updateSchedule();
  }

  function handleStartFocus() {
    if (!selectedTask) return;
    const detail = { taskId: selectedTask.id, preset: selectedFocusPreset };
    window.dispatchEvent(new CustomEvent('blooming:start-focus', { detail }));
  }

  function dispatchAction(name: 'edit-schedule' | 'replan-schedule') {
    window.dispatchEvent(new CustomEvent(`blooming:${name}`));
  }
</script>

<div class="today-page">
  <div class="today-window">
    <DesktopTitleBar />
    <div class="today-content">
      <AppSidebar activeRoute="TODAY" />
      <main class="today-main">
        <TodayTimeline
          {tasks}
          {currentDate}
          {selectedTaskId}
          onSelect={(id) => (selectedTaskId = id)}
          onDateChange={handleDateChange}
        />
        <BottomActions
          onEdit={() => dispatchAction('edit-schedule')}
          onReplan={() => dispatchAction('replan-schedule')}
        />
      </main>
      <aside class="today-rail">
        <RightRail
          task={selectedTask}
          {nextTask}
          {selectedFocusPreset}
          onPresetSelect={(preset) => (selectedFocusPreset = preset)}
          onStartFocus={handleStartFocus}
        />
      </aside>
    </div>
  </div>
</div>

<style>
  .today-page {
    --bloom-body-font: "Cascadia Mono", "Lucida Console", Consolas, monospace;
    --bloom-display-font: "Cascadia Mono", "Lucida Console", Consolas, monospace;
    display: grid;
    width: 100vw;
    height: 100vh;
    min-width: 1220px;
    min-height: 800px;
    place-items: center;
    overflow: auto;
    background: #fbfaf5;
  }

  .today-window {
    display: flex;
    width: min(1400px, calc(100vw - 40px));
    height: min(874px, calc(100vh - 26px));
    min-width: 1180px;
    min-height: 774px;
    flex-direction: column;
    overflow: hidden;
    border: 2px solid #0b516b;
    border-radius: 8px;
    background: #f5eddc;
    box-shadow: 0 0 0 1px #29b9ce, inset 0 0 0 1px #d8f6f4;
  }

  .today-window :global(.desktop-titlebar) {
    height: 42px;
    flex-basis: 42px;
    border-bottom-width: 2px;
    background: linear-gradient(180deg, #2796ad 0%, #278aa1 100%);
    box-shadow: inset 0 2px 0 #40d2df;
  }
  .today-window :global(.desktop-titlebar__logo) { width: 35px; height: 35px; }
  .today-window :global(.desktop-titlebar__title) { font-size: 21px; }
  .today-window :global(.desktop-window-control) { width: 29px; height: 28px; }
  .today-window :global(.desktop-titlebar__controls) { gap: 7px; padding-right: 9px; }

  .today-content {
    display: grid;
    min-height: 0;
    flex: 1;
    grid-template-columns: 176px minmax(0, 1fr) 434px;
    gap: 9px;
    padding: 9px 9px 10px 0;
  }
  .today-main {
    display: flex;
    min-width: 0;
    min-height: 0;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid #cbc6b9;
    border-radius: 5px;
    background: rgba(255, 253, 247, 0.72);
  }
  .today-rail { min-width: 0; min-height: 0; }

  @media (max-width: 1250px), (max-height: 820px) {
    .today-page { place-items: start; padding: 12px 20px; }
    .today-window { width: 1180px; height: 774px; }
    .today-content { grid-template-columns: 155px minmax(0, 1fr) 390px; }
  }
</style>
