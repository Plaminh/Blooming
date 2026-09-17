import type { FocusingPresentation } from "../types/presentation";
import { DEFAULT_ACTIVE_PLANT } from "./scene";

export const focusingFixture: FocusingPresentation = {
  kind: "focusing",
  activePlant: DEFAULT_ACTIVE_PLANT,
  timeText: "23:45",
  onPause: () => {},
  onEnd: () => {},
};
