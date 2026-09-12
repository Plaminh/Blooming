import type { ActivePlantPresentation } from "../types/presentation";

export const DEFAULT_ACTIVE_PLANT: ActivePlantPresentation = {
  species: "monstera",
  frameIndex: 7,
};

export const DEFAULT_WIDGET_SCENE = {
  activePlant: DEFAULT_ACTIVE_PLANT,
};
