import type { EndingPresentation } from "../types/presentation";
import { DEFAULT_ACTIVE_PLANT } from "./scene";

export const endingFixture: EndingPresentation = {
  kind: "ending",
  activePlant: DEFAULT_ACTIVE_PLANT,
  speechText: "Time's up! How did it go?",
  timeText: "00:00",
  onDone: () => {},
  onFinishedEarly: () => {},
  onNeedMoreTime: () => {},
  onSkip: () => {},
};
