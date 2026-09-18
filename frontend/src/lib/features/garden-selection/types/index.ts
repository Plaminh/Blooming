export type { PlantSpecies } from "$lib/features/companion-widget/types/presentation";
import type { PlantSpecies } from "$lib/features/companion-widget/types/presentation";
export type PlantId = string;

export interface PlantPresentation {
  id: PlantId;
  name: string;
  description: string[];
  species: PlantSpecies;
  unlockCost: number;
}
