<script lang="ts">
  import DesktopAppShell from '$lib/shared/components/organisms/DesktopAppShell.svelte';
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

<DesktopAppShell activeRoute="TODAY" variant="compact">
  <div class="today-content">
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
</DesktopAppShell>

<style>
  .today-content {
    display: grid;
    width: 100%;
    height: 100%;
    min-height: 0;
    grid-template-columns: minmax(0, 1fr) 390px;
    gap: 9px;
    padding: 9px 9px 10px 0;
  }
  .today-main {
    display: flex;
    min-width: 0;
    min-height: 0;
    flex-direction: column;
    overflow: hidden;
  }
  .today-rail { min-width: 0; min-height: 0; }

</style>
