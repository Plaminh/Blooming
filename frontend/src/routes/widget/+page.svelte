<script lang="ts">
  import { CompanionWidget } from "$lib/features/companion-widget";
  import type {
    CompanionWidgetPresentation,
    ActivePlantPresentation,
  } from "$lib/features/companion-widget/types/presentation";
  import { onMount } from "svelte";
  import { api, APIError } from "$lib/api";
  import type { GardenState, TodayResponse } from "$lib/api/types";
  import { selectedPlantPresentation } from "$lib/features/garden/utils/spriteMapper";
  import { desktop } from "$lib/platform/desktopWindow";
  import type { UserSettingsResponse } from "$lib/api/types";
  import type { Weather } from "$lib/features/companion-widget/model/environment";

  interface FocusSession {
    id: string;
    task_id?: string;
    status: string;
    started_at: string;
    paused_at?: string;
    total_paused_seconds: number;
    planned_focus_seconds: number;
  }

  let activeSession: FocusSession | null = $state(null);
  let now = $state(new Date());
  let isPending = $state(false);
  let isEndingLocal = $state(false);
  let activePlant = $state<ActivePlantPresentation | null>(null);
  let lastSessionId: string | null = null;
  let endRequested = $state(false);
  let completedSessionId: string | null = null;
  let fetching = false;
  let finishWarning = $state<string | null>(null);
  let finishError = $state<string | null>(null);
  let timezone = $state("UTC");
  let weather = $state<Weather>("CLEAR");
  let rainEnabled = $state(true);
  const ENVIRONMENT_REFRESH_MS = 15 * 60 * 1000;
  let environmentRequestId = 0;

  async function refreshEnvironment() {
    const requestId = ++environmentRequestId;
    try {
      const settings: UserSettingsResponse = await api.get("/me/settings");
      if (requestId !== environmentRequestId) return;
      timezone = settings.timezone;
      rainEnabled = settings.weather_animation_enabled !== false;
      if (settings.weather_enabled && settings.weather_location?.trim()) {
        const response: { condition: Weather } = await api.get("/me/weather");
        if (requestId === environmentRequestId) weather = response.condition;
      } else {
        weather = "CLEAR";
      }
    } catch {
      if (requestId === environmentRequestId) weather = "CLEAR";
    }
  }

  async function fetchSession() {
    if (fetching) return;
    fetching = true;
    try {
      const session: FocusSession | null = await api.get("/focus/active");
      if (session && session.id !== lastSessionId) {
        lastSessionId = session.id;
        endRequested = false;
        isEndingLocal = false;
        completedSessionId = null;
        finishError = null;
      }
      activeSession = session;
    } catch (error: unknown) {
      if (error instanceof APIError && error.status === 404)
        activeSession = null;
      else
        finishError =
          error instanceof Error
            ? error.message
            : "Unable to load focus session.";
    }
    try {
      const garden: GardenState = await api.get("/garden");
      activePlant = selectedPlantPresentation(garden);
    } catch {
      activePlant = null;
    } finally {
      fetching = false;
    }
  }

  onMount(() => {
    void fetchSession();
    void refreshEnvironment();
    const environmentRefresh = setInterval(() => void refreshEnvironment(), ENVIRONMENT_REFRESH_MS);
    const clock = setInterval(() => {
      now = new Date();
    }, 1000);
    const refresh = setInterval(() => void fetchSession(), 60000);
    let disposed = false;
    let unlisten = () => {};
    let unlistenSettings = () => {};
    const refreshSettings = () => void refreshEnvironment();
    window.addEventListener("storage", refreshSettings);
    window.addEventListener("focus", refreshSettings);
    desktop
      .onSettingsUpdated(refreshSettings)
      .then((off) => {
        if (disposed) off();
        else unlistenSettings = off;
      })
      .catch(() => {});
    desktop
      .onScheduleUpdated(() => void fetchSession())
      .then((off) => {
        if (disposed) off();
        else unlisten = off;
      })
      .catch((error: unknown) => {
        finishError =
          error instanceof Error
            ? error.message
            : "Widget synchronization unavailable.";
      });
    return () => {
      disposed = true;
      unlisten();
      unlistenSettings();
      window.removeEventListener("storage", refreshSettings);
      window.removeEventListener("focus", refreshSettings);
      clearInterval(clock);
      clearInterval(refresh);
      clearInterval(environmentRefresh);
    };
  });

  const remainingSeconds = $derived.by(() => {
    if (!activeSession) return 0;
    const until =
      activeSession.status === "PAUSED" && activeSession.paused_at
        ? new Date(activeSession.paused_at)
        : now;
    const elapsed =
      Math.floor(
        (until.getTime() - new Date(activeSession.started_at).getTime()) / 1000,
      ) - activeSession.total_paused_seconds;
    return Math.max(0, activeSession.planned_focus_seconds - elapsed);
  });
  $effect(() => {
    if (
      activeSession &&
      activeSession.status !== "PAUSED" &&
      remainingSeconds === 0 &&
      !endRequested
    ) {
      endRequested = true;
      isEndingLocal = true;
    }
  });

  async function handlePause() {
    if (isPending) return;
    isPending = true;
    try {
      await api.post("/focus/pause");
      await fetchSession();
    } finally {
      isPending = false;
    }
  }

  async function handleResume() {
    if (isPending) return;
    isPending = true;
    try {
      await api.post("/focus/resume");
      await fetchSession();
    } finally {
      isPending = false;
    }
  }

  function handleEnd() {
    if (endRequested) return;
    endRequested = true;
    isEndingLocal = true;
  }

  async function handleFinish(outcome: string) {
    if (isPending || !activeSession || completedSessionId === activeSession.id)
      return;
    const session = activeSession;
    endRequested = true;
    isPending = true;
    finishError = null;
    const previousEndingLocal = isEndingLocal;
    try {
      const result: { replan?: TodayResponse | null } = await api.post("/focus/finish", {
        run_id: session.id,
        outcome,
        should_replan: true,
      });
      finishWarning = result.replan?.unscheduled_tasks?.length
        ? `Focus saved. ${result.replan.unscheduled_tasks.length} task(s) need manual scheduling. Open Today for details.`
        : null;
      completedSessionId = session.id;
      activeSession = null;
      isEndingLocal = false;
      try {
        await desktop.scheduleUpdated();
        if (!finishWarning) await desktop.hideCurrent();
      } catch {
        finishWarning = [finishWarning, "Focus saved, but window synchronization failed."].filter(Boolean).join(" ");
      }
      await fetchSession();
    } catch (err: unknown) {
      isEndingLocal = previousEndingLocal;
      finishError =
        err instanceof Error ? err.message : "Failed to complete session.";
      console.error("Failed to finish focus session", err);
    } finally {
      isPending = false;
    }
  }

  let presentation = $derived.by<CompanionWidgetPresentation>(() => {
    if (!activeSession) {
      return {
        kind: "offline",
        activePlant,
        speechText: finishWarning ?? "Waiting for a focus session...",
      };
    }

    if (isEndingLocal) {
      return {
        kind: "ending",
        activePlant,
        speechText: finishError
          ? `Error: ${finishError} Try again.`
          : "Session ended. What was the outcome?",
        onDone: () => handleFinish("DONE"),
        onFinishedEarly: () => handleFinish("FINISHED_EARLY"),
        onNeedMoreTime: () => handleFinish("NEED_MORE_TIME"),
        onSkip: () => handleFinish("SKIP"),
      };
    }

    const mins = Math.floor(remainingSeconds / 60);
    const secs = remainingSeconds % 60;
    const timeText = `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;

    if (activeSession.status === "PAUSED") {
      return {
        kind: "paused",
        activePlant,
        timeText,
        speechText: "Take your time...",
        onResume: handleResume,
        onEnd: handleEnd,
      };
    }

    return {
      kind: "focusing",
      activePlant,
      timeText,
      onPause: handlePause,
      onEnd: handleEnd,
    };
  });
</script>

{#if finishError}<p role="alert">{finishError}</p>{/if}
<CompanionWidget {presentation} {weather} {timezone} {rainEnabled} />
