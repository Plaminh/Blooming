<script lang="ts">
  import { CompanionWidget } from "$lib/features/companion-widget";
  import type { CompanionWidgetPresentation, FocusingPresentation, EndingPresentation, PausedPresentation } from "$lib/features/companion-widget/types/presentation";
  import { onMount, onDestroy } from "svelte";
  import { api } from "$lib/api";

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
  let timerInterval: number | ReturnType<typeof setInterval>;
  let isPending = $state(false);
  let isEndingLocal = $state(false);
  
  const activePlant = { species: "monstera" as const, frameIndex: 0 as const };

  async function fetchSession() {
    try {
      const data = (await api.get('/focus/active')) as FocusSession;
      activeSession = data;
    } catch (err: any) {
      if (err?.status === 404 || err?.response?.status === 404 || err?.message?.includes('404')) {
        activeSession = null;
      } else {
        console.error("Failed to fetch active session", err);
      }
    }
  }

  onMount(() => {
    fetchSession();
    timerInterval = setInterval(() => {
      now = new Date();
    }, 1000);
    
    // Listen for global events if needed
    const handleReplan = () => fetchSession();
    window.addEventListener('blooming:replan-schedule', handleReplan);
    return () => {
      window.removeEventListener('blooming:replan-schedule', handleReplan);
    };
  });

  onDestroy(() => {
    clearInterval(timerInterval as number);
  });

  async function handlePause() {
    if (isPending) return;
    isPending = true;
    try {
      await api.post('/focus/pause');
      await fetchSession();
    } finally {
      isPending = false;
    }
  }

  async function handleResume() {
    if (isPending) return;
    isPending = true;
    try {
      await api.post('/focus/resume');
      await fetchSession();
    } finally {
      isPending = false;
    }
  }

  function handleEnd() {
    isEndingLocal = true;
  }

  let finishError = $state<string | null>(null);

  async function handleFinish(outcome: string) {
    if (isPending) return;
    isPending = true;
    finishError = null;
    const previousEndingLocal = isEndingLocal;
    try {
      const startedAt = new Date(activeSession!.started_at);
      let elapsedSeconds = 0;
      
      if (activeSession!.status === "PAUSED" && activeSession!.paused_at) {
         const pausedAt = new Date(activeSession!.paused_at);
         elapsedSeconds = Math.floor((pausedAt.getTime() - startedAt.getTime()) / 1000) - activeSession!.total_paused_seconds;
      } else {
         elapsedSeconds = Math.floor((now.getTime() - startedAt.getTime()) / 1000) - activeSession!.total_paused_seconds;
      }
      const actualDurationSeconds = Math.max(0, elapsedSeconds);

      await api.post('/focus/finish', {
        outcome,
        actual_duration_seconds: actualDurationSeconds,
        should_replan: true
      });
      isEndingLocal = false;
      if (typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window) {
        import('@tauri-apps/api/window').then(({ Window }) => {
          Window.getByLabel('companion-widget').then(w => w?.hide());
        });
      }
      await fetchSession();
    } catch (err: any) {
      isEndingLocal = previousEndingLocal;
      finishError = err.message || 'Failed to complete session.';
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
        speechText: "Waiting for a focus session..."
      };
    }

    if (isEndingLocal) {
      return {
        kind: "ending",
        activePlant,
        speechText: finishError ? `Error: ${finishError} Try again.` : "Session ended. What was the outcome?",
        onDone: () => handleFinish('DONE'),
        onFinishedEarly: () => handleFinish('FINISHED_EARLY'),
        onNeedMoreTime: () => handleFinish('NEED_MORE_TIME'),
        onSkip: () => handleFinish('SKIP')
      } as EndingPresentation;
    }

    const startedAt = new Date(activeSession.started_at);
    let elapsedSeconds = 0;
    
    if (activeSession.status === "PAUSED" && activeSession.paused_at) {
       const pausedAt = new Date(activeSession.paused_at);
       elapsedSeconds = Math.floor((pausedAt.getTime() - startedAt.getTime()) / 1000) - activeSession.total_paused_seconds;
    } else {
       elapsedSeconds = Math.floor((now.getTime() - startedAt.getTime()) / 1000) - activeSession.total_paused_seconds;
    }

    const remainingSeconds = Math.max(0, activeSession.planned_focus_seconds - elapsedSeconds);
    const mins = Math.floor(remainingSeconds / 60);
    const secs = remainingSeconds % 60;
    const timeText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

    if (activeSession.status === "PAUSED") {
      return {
        kind: "paused",
        activePlant,
        timeText,
        speechText: "Take your time...",
        onResume: handleResume,
        onEnd: handleEnd
      } as PausedPresentation;
    }

    return {
      kind: "focusing",
      activePlant,
      timeText,
      onPause: handlePause,
      onEnd: handleEnd
    } as FocusingPresentation;
  });
</script>

<CompanionWidget {presentation} />
