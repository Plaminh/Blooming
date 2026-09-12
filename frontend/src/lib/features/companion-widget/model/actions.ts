import type { CompanionWidgetPresentation, WidgetAction } from "../types/presentation";

export function actionsFor(
  presentation: CompanionWidgetPresentation,
): WidgetAction[] {
  switch (presentation.kind) {
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
          id: "view",
          label: "VIEW",
          variant: "primary",
          onClick: presentation.onView,
        },
        {
          id: "dismiss",
          label: "DISMISS",
          variant: "secondary",
          onClick: presentation.onDismiss,
        },
      ];
    case "offline":
      return [];
  }
}
