import type { BehindSchedulePresentation } from "../types/presentation";

export const behindScheduleFixture: BehindSchedulePresentation = {
  kind: "behindSchedule",
  speechText: "We are 35 minutes behind. Adjust the remaining plan?",
  activePlant: { species: "sunflower", frameIndex: 11 },
  onReplan: () => {},
  onLater: () => {},
  onOpen: () => {},
};
