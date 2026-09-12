import type { PausedPresentation } from "../types/presentation";

export const pausedFixture: PausedPresentation = {
  kind: "paused",
  speechText: "Paused. Take your time.",
  timeText: "18:42",
  activePlant: { species: "monstera", frameIndex: 7 },
  onResume: () => {},
  onEnd: () => {},
};
