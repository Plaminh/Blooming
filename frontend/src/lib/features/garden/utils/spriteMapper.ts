import type { GrowthStage, GardenState } from "$lib/api/types";
import type {
  PlantFrameIndex,
  PlantSpecies,
  ActivePlantPresentation,
} from "$lib/features/companion-widget/types/presentation";
import {
  PLANT_SOURCES,
  PLANT_SPECIES,
} from "$lib/features/companion-widget/model/plants";

export type PlantVitality = "HEALTHY" | "THIRSTY" | "WILTING" | "DORMANT";

export const PLANT_SPRITE_CONFIG = Object.fromEntries(
  PLANT_SPECIES.map((species) => [species, { src: PLANT_SOURCES[species] }]),
) as Record<PlantSpecies, { src: string }>;

const GROWTH_ROW: Record<GrowthStage, number> = {
  SPROUTING: 0,
  GROWING: 1,
  BLOOMING: 2,
  FLOURISHING: 3,
};

const VITALITY_COLUMN: Record<PlantVitality, number> = {
  HEALTHY: 0,
  THIRSTY: 1,
  WILTING: 2,
  DORMANT: 3,
};

export function isPlantSpecies(value: string): value is PlantSpecies {
  return PLANT_SPECIES.some((species) => species === value);
}

export function vitalityState(vitality: number): PlantVitality {
  if (!Number.isFinite(vitality) || vitality <= 0) return "DORMANT";
  if (vitality < 25) return "DORMANT";
  if (vitality < 50) return "WILTING";
  if (vitality < 75) return "THIRSTY";
  return "HEALTHY";
}

export function getPlantFrame(
  _species: PlantSpecies,
  stage: GrowthStage,
  vitality: number,
): PlantFrameIndex {
  const row = GROWTH_ROW[stage] ?? GROWTH_ROW.SPROUTING;
  return (row * 4 + VITALITY_COLUMN[vitalityState(vitality)]) as PlantFrameIndex;
}

export function selectedPlantPresentation(
  garden: GardenState,
): ActivePlantPresentation | null {
  const plant = garden.catalog.find(
    (item) => item.id === garden.selected_plant_id,
  );
  if (!plant || !isPlantSpecies(plant.species)) return null;
  return {
    species: plant.species,
    scale: 1,
    frameIndex: getPlantFrame(
      plant.species,
      garden.growth_stage,
      garden.vitality,
    ),
  };
}
