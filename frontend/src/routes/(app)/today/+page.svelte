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

  let currentDate = $state(new Date());
  let tasks = $state<Task[]>([]);
  let selectedTaskId = $state('');
  let selectedFocusPreset = $state<FocusPreset>('25/5');
  let isPending = $state(false);
  let isLoading = $state(false);
  let loadError = $state<string | null>(null);

  const selectedTask = $derived(tasks.find((task) => task.id === selectedTaskId));
  const nextTask = $derived(tasks.find((task) => task.status === 'upcoming'));

  let currentRequestId = 0;

  async function updateSchedule() {
    const reqId = ++currentRequestId;
    isLoading = true;
    loadError = null;

    try {
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const isoDate = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}`;
      
      const params = new URLSearchParams({
        date: isoDate,
        tz: tz
      });
      
      const data = (await api.get(`/today?${params.toString()}`)) as { blocks: PlanBlock[] };
      
      if (reqId !== currentRequestId) return;

      if (data && data.blocks) {
         tasks = data.blocks.map((b: PlanBlock) => {
            let start = new Date();
            let end = new Date();
            try {
              if (b.planned_start_at) start = new Date(b.planned_start_at);
              if (b.planned_end_at) end = new Date(b.planned_end_at);
            } catch (e) {
              // ignore invalid dates, use current time
            }
            
            const durationMins = Math.round((end.getTime() - start.getTime()) / 60000) || 0;

            return {
              id: b.id, // block ID
              task_id: b.task_id || null, // actual task ID or null for break
              title: b.title || (b.block_type === 'BREAK' ? 'Break' : 'Unknown'),
              startTime: start.toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit', hour12: false}),
              endTime: end.toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit', hour12: false}),
              durationString: `(${Math.max(0, durationMins)} min)`,
              status: b.status === 'COMPLETED' ? 'completed' : b.status === 'ACTIVE' ? 'in-progress' : 'upcoming',
              category: 'Work',
              iconRef: b.block_type === 'BREAK' ? 'break' : 'document',
              description: '',
              notes: ''
            };
         });
      } else {
         tasks = [];
      }
      
      if (tasks.length === 0) {
         selectedTaskId = '';
      } else if (!tasks.find((t) => t.id === selectedTaskId)) {
         selectedTaskId = tasks[0]?.id ?? '';
      }
    } catch (err) {
      if (reqId !== currentRequestId) return;
      loadError = 'Failed to load today plan.';
      tasks = [];
      selectedTaskId = '';
    } finally {
      if (reqId === currentRequestId) {
        isLoading = false;
      }
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
    if (!selectedTask || isPending || !selectedTask.task_id) return;
    isPending = true;
    
    let focusMinutes = 25;
    let breakMinutes = 5;
    if (selectedFocusPreset === '50/10') { focusMinutes = 50; breakMinutes = 10; }

    try {
      await api.post('/focus/start', {
        task_id: selectedTask.task_id, // Send task_id, not block id
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
      // surface to UI?
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
      {isLoading}
      {loadError}
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
