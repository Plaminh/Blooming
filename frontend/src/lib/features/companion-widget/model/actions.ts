import type { CompanionWidgetPresentation, WidgetAction } from "../types/presentation";

export function actionsFor(
  presentation: CompanionWidgetPresentation,
): WidgetAction[] {
  switch (presentation.kind) {
    case "focusing":
      return [
        { id: "pause", label: "PAUSE", variant: "primary", icon: "stop", onClick: presentation.onPause },
        { id: "end", label: "END", variant: "secondary", onClick: presentation.onEnd },
      ];
    case "ending":
      return [
        { id: "done", label: "DONE", variant: "primary", onClick: presentation.onDone },
        { id: "early", label: "FINISHED EARLY", variant: "primary", onClick: presentation.onFinishedEarly },
        { id: "more", label: "NEED MORE TIME", variant: "secondary", onClick: presentation.onNeedMoreTime },
        { id: "skip", label: "SKIP", variant: "secondary", onClick: presentation.onSkip },
      ];
    case "paused":
      return [
        {
          id: "resume",
          label: "RESUME",
          variant: "primary",
          icon: "play",
          onClick: presentation.onResume,
        },
        {
          id: "end",
          label: "END",
          variant: "secondary",
          icon: "stop",
          onClick: presentation.onEnd,
        },
      ];
    case "behindSchedule":
      return [
        {
          id: "replan",
          label: "REPLAN",
          variant: "primary",
          onClick: presentation.onReplan,
        },
        {
          id: "later",
          label: "LATER",
          variant: "secondary",
          onClick: presentation.onLater,
        },
        {
          id: "open",
          label: "OPEN",
          variant: "secondary",
          onClick: presentation.onOpen,
        },
      ];
    case "reminders":
      return [
        {
          id: "create_plan",
          label: "CREATE PLAN",
          variant: "primary",
          onClick: presentation.onCreatePlan,
        },
        {
          id: "mark_completed",
          label: "MARK COMPLETED",
          variant: "primary",
          onClick: presentation.onMarkCompleted,
        },
        {
          id: "move_milestone",
          label: "MOVE MILESTONE",
          variant: "secondary",
          onClick: presentation.onMoveMilestone,
        },
        {
          id: "remind_later",
          label: "REMIND LATER",
          variant: "secondary",
          onClick: presentation.onRemindLater,
        },
      ];
    case "offline":
      return [];
  }
}
