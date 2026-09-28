export type { PlantSpecies } from '$lib/shared/sprites/types';
import type { PlantSpecies } from '$lib/shared/sprites/types';
export type PlantId = string;

export interface PlantPresentation {
  id: PlantId;
  name: string;
  description: string[];
  species: PlantSpecies;
  unlockCost: number;
}
