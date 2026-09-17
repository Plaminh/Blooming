<script lang="ts">
  import BottomActions from '$lib/features/today/components/organisms/BottomActions.svelte';
  import RightRail from '$lib/features/today/components/organisms/RightRail.svelte';
  import TodayTimeline from '$lib/features/today/components/organisms/TodayTimeline.svelte';
  import type { FocusPreset, Task } from '$lib/features/today/types';
  import { api } from '$lib/api';

  interface PlanBlock {
    id: string;
    task_id?: string;
    title?: string;
    planned_start_at: string;
    planned_end_at: string;
    status: string;
    block_type: string;
  }

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
  let isPending = $state(false);

  const selectedTask = $derived(tasks.find((task) => task.id === selectedTaskId));
  const nextTask = $derived(tasks.find((task) => task.status === 'upcoming'));

  async function updateSchedule() {
    try {
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const isoDate = currentDate.toISOString().split('T')[0];
      const data = (await api.get(`/today?date=${isoDate}&tz=${tz}`)) as { blocks: PlanBlock[] };
      if (data && data.blocks) {
         tasks = data.blocks.map((b: PlanBlock) => ({
            id: b.task_id || b.id,
            title: b.title || 'Unknown',
            startTime: new Date(b.planned_start_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
            endTime: new Date(b.planned_end_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
            durationString: `(${Math.round((new Date(b.planned_end_at).getTime() - new Date(b.planned_start_at).getTime()) / 60000)} min)`,
            status: b.status === 'COMPLETED' ? 'completed' : b.status === 'ACTIVE' ? 'in-progress' : 'upcoming',
            category: 'Work',
            iconRef: b.block_type === 'BREAK' ? 'break' : 'document',
            description: '',
            notes: ''
         }));
      } else {
         tasks = [];
      }
      if (!tasks.find((t) => t.id === selectedTaskId)) {
         selectedTaskId = tasks[0]?.id ?? '';
      }
    } catch (err) {
      console.error("Failed to load today plan", err);
      tasks = [];
    }
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

  $effect(() => {
    updateSchedule();
  });

  async function handleStartFocus() {
    if (!selectedTask || isPending) return;
    isPending = true;
    
    let focusMinutes = 25;
    let breakMinutes = 5;
    if (selectedFocusPreset === '50/10') { focusMinutes = 50; breakMinutes = 10; }

    try {
      await api.post('/focus/start', {
        task_id: selectedTask.id,
        planned_focus_seconds: focusMinutes * 60,
        planned_break_seconds: breakMinutes * 60
      });
      
      if (typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window) {
         const { Window } = await import('@tauri-apps/api/window');
         const widget = await Window.getByLabel('companion-widget');
         if (widget) {
            await widget.show();
            await widget.setFocus();
         }
      }
      await updateSchedule();
    } catch (err) {
      console.error("Failed to start focus session", err);
    } finally {
      isPending = false;
    }
  }

  function dispatchAction(name: 'edit-schedule' | 'replan-schedule') {
    window.dispatchEvent(new CustomEvent(`blooming:${name}`));
  }
</script>

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
