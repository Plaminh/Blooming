import type { RemindersPresentation } from "../types/presentation";

export const remindersFixture: RemindersPresentation = {
  kind: "reminders",
  activePlant: { species: "jasmine", frameIndex: 10 },
  reminders: [
    { id: "start-database", label: "Start Database" },
    { id: "review-milestone", label: "Review milestone" },
  ],
  onCreatePlan: () => {},
  onMarkCompleted: () => {},
  onMoveMilestone: () => {},
  onRemindLater: () => {},
};
