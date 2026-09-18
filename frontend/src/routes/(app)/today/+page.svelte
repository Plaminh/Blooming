<script lang="ts">
  import BottomActions from "$lib/features/today/components/organisms/BottomActions.svelte";
  import RightRail from "$lib/features/today/components/organisms/RightRail.svelte";
  import TodayTimeline from "$lib/features/today/components/organisms/TodayTimeline.svelte";
  import type { FocusPreset, Task } from "$lib/features/today/types";
  import { api } from "$lib/api";

  import type { TodayResponse, TodayTaskEdit } from "$lib/api/types";
  import { desktop } from "$lib/platform/desktopWindow";
  import { onMount } from "svelte";
  let rail: RightRail;

  let currentDate = $state(new Date());
  let requestedDate = $state<string | null>(null);
  let planTimezone = $state("UTC");
  let replanWarning = $state<string | null>(null);
  let tasks = $state<Task[]>([]);
  let selectedTaskId = $state("");
  let selectedFocusPreset = $state<FocusPreset>("25/5");
  let isPending = $state(false);
  let focusStarted = $state(false);
  let isLoading = $state(false);
  let loadError = $state<string | null>(null);

  const selectedTask = $derived(
    tasks.find((task) => task.id === selectedTaskId),
  );
  const nextTask = $derived(tasks.find((task) => task.status === "upcoming"));

  let currentRequestId = 0;

  async function updateSchedule() {
    const reqId = ++currentRequestId;
    isLoading = true;
    loadError = null;

    try {
      const data: TodayResponse = await api.get(requestedDate ? `/today?date=${requestedDate}` : "/today");

      if (reqId !== currentRequestId) return;

      applySchedule(data);
    } catch (err) {
      if (reqId !== currentRequestId) return;
      loadError = "Failed to load today plan.";
    } finally {
      if (reqId === currentRequestId) {
        isLoading = false;
      }
    }
  }

  function applySchedule(data: TodayResponse) {
    planTimezone = data.timezone ?? "UTC";
    const [year, month, day] = data.plan_date.split("-").map(Number);
    currentDate = new Date(year, month - 1, day, 12);
    replanWarning = data.unscheduled_tasks?.length
      ? `${data.unscheduled_tasks.length} task(s) could not be scheduled. Completed work is saved. Adjust availability and replan. ${data.reasons?.map((reason) => `${reason.task_id}: ${reason.code}${reason.dependency_id ? ` (dependency ${reason.dependency_id})` : ""}`).join("; ") ?? ""}`
      : null;
    if (data.status !== "NO_PLAN" && data.blocks) {
      tasks = data.blocks.map((b) => {
        let start = new Date();
        let end = new Date();
        try {
          if (b.planned_start_at) start = new Date(b.planned_start_at);
          if (b.planned_end_at) end = new Date(b.planned_end_at);
        } catch (e) {
          // ignore invalid dates, use current time
        }

        const durationMins =
          Math.round((end.getTime() - start.getTime()) / 60000) || 0;

        return {
          id: b.id, // block ID
          task_id: b.task_id || null, // actual task ID or null for break
          title: b.title || (b.block_type === "BREAK" ? "Break" : "Unknown"),
          startTime: start.toLocaleTimeString("en-GB", {
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
            timeZone: planTimezone,
          }),
          endTime: end.toLocaleTimeString("en-GB", {
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
            timeZone: planTimezone,
          }),
          durationString: `(${Math.max(0, durationMins)} min)`,
          estimatedDurationMinutes:
            b.estimated_duration_minutes ?? durationMins,
          status:
            b.status === "COMPLETED"
              ? "completed"
              : b.status === "ACTIVE"
                ? "in-progress"
                : "upcoming",
          category: b.category ?? null,
          iconRef: b.block_type === "BREAK" ? "break" : "document",
          description: b.description || "",
          notes: b.description || "",
        };
      });
    } else {
      tasks = [];
    }

    if (tasks.length === 0) {
      selectedTaskId = "";
    } else if (!tasks.find((t) => t.id === selectedTaskId)) {
      selectedTaskId = tasks[0]?.id ?? "";
    }
  }

  function handleDateChange(offset: number) {
    if (offset === 0) {
      requestedDate = null;
    } else {
      const nextDate = new Date(currentDate);
      nextDate.setDate(nextDate.getDate() + offset);
      currentDate = nextDate;
      requestedDate = `${nextDate.getFullYear()}-${String(nextDate.getMonth() + 1).padStart(2, "0")}-${String(nextDate.getDate()).padStart(2, "0")}`;
    }
    updateSchedule();
  }

  onMount(() => {
    void updateSchedule();
    let disposed = false;
    let cleanup = () => {};
    desktop
      .onScheduleUpdated(() => {
        focusStarted = false;
        void updateSchedule();
      })
      .then((off) => {
        if (disposed) off();
        else cleanup = off;
      })
      .catch((error: unknown) => {
        syncWarning =
          error instanceof Error
            ? error.message
            : "Widget synchronization unavailable.";
      });
    return () => {
      disposed = true;
      cleanup();
    };
  });

  let actionError = $state<string | null>(null);
  let syncWarning = $state<string | null>(null);

  async function syncWidget(message: string, showWidget = false) {
    const results = await Promise.allSettled([
      desktop.scheduleUpdated(),
      ...(showWidget ? [desktop.showWidget()] : []),
    ]);
    if (results.some((result) => result.status === "rejected")) {
      syncWarning = message;
    }
  }

  async function handleSaveTask(id: string, updates: TodayTaskEdit) {
    syncWarning = null;
    await api.patch(`/today/tasks/${id}`, updates);
    tasks = tasks.map((task) =>
      task.task_id === id
        ? {
            ...task,
            title: updates.title ?? task.title,
            estimatedDurationMinutes:
              updates.estimated_duration_minutes ??
              task.estimatedDurationMinutes,
            category:
              updates.category === undefined ? task.category : updates.category,
            description:
              updates.description === undefined
                ? task.description
                : (updates.description ?? ""),
            notes:
              updates.description === undefined
                ? task.notes
                : (updates.description ?? ""),
          }
        : task,
    );
    // Resolve the editor save before attempting cross-window synchronization.
    void syncWidget("Saved, but widget sync failed.");
  }

  async function handleStartFocus() {
    if (!selectedTask || isPending || focusStarted || !selectedTask.task_id)
      return;
    isPending = true;
    actionError = null;
    syncWarning = null;

    let focusMinutes = 25;
    let breakMinutes = 5;
    if (selectedFocusPreset === "50/10") {
      focusMinutes = 50;
      breakMinutes = 10;
    }

    try {
      await api.post("/focus/start", {
        task_id: selectedTask.task_id, // Send task_id, not block id
        planned_focus_seconds: focusMinutes * 60,
        planned_break_seconds: breakMinutes * 60,
      });

      focusStarted = true;
      const startedTaskId = selectedTask.task_id;
      tasks = tasks.map((task) =>
        task.task_id === startedTaskId
          ? { ...task, status: "in-progress" }
          : task,
      );
      await updateSchedule();
      await syncWidget("Focus started, but widget sync failed.", true);
    } catch (err: unknown) {
      actionError =
        err instanceof Error ? err.message : "Failed to start focus session.";
    } finally {
      isPending = false;
    }
  }

  async function handleReplan() {
    if (isPending) return;
    isPending = true;
    actionError = null;
    syncWarning = null;
    try {
      const data: TodayResponse = await api.post("/today/replan");
      ++currentRequestId;
      isLoading = false;
      loadError = null;
      requestedDate = null;
      applySchedule(data);
      await syncWidget("Replanned, but widget sync failed.");
    } catch (err: unknown) {
      actionError =
        err instanceof Error
          ? err.message
          : "Failed to replan. Please try again.";
    } finally {
      isPending = false;
    }
  }
</script>

<div class="today-content">
  {#if replanWarning}
    <div class="toast-error" role="status" aria-live="polite">{replanWarning}</div>
  {/if}
  {#if syncWarning}
    <div class="toast-error" role="status" aria-live="polite">
      {syncWarning}
      <button aria-label="Dismiss warning" onclick={() => (syncWarning = null)}
        >×</button
      >
    </div>
  {/if}
  {#if actionError}
    <div class="toast-error" role="alert" aria-live="assertive">
      {actionError}
      <button aria-label="Close" onclick={() => (actionError = null)}>×</button>
    </div>
  {/if}
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
      onEdit={() => rail?.startEditing()}
      onReplan={handleReplan}
      disabled={isPending}
    />
  </main>
  <aside class="today-rail">
    <RightRail
      bind:this={rail}
      task={selectedTask}
      {nextTask}
      {selectedFocusPreset}
      onPresetSelect={(preset) => (selectedFocusPreset = preset)}
      onStartFocus={handleStartFocus}
      focusDisabled={isPending || focusStarted}
      onSaveTask={handleSaveTask}
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
  .today-rail {
    min-width: 0;
    min-height: 0;
  }
  .toast-error {
    position: absolute;
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--bloom-error, #fde8e8);
    color: var(--bloom-text-dark-blue, #064798);
    padding: 12px 24px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 100;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .toast-error button {
    background: transparent;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: inherit;
  }
</style>
