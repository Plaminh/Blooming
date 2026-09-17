import type { GrowthStage, GardenState } from "$lib/api/types";
import type {
  PlantFrameIndex,
  PlantSpecies,
  ActivePlantPresentation,
} from "$lib/features/companion-widget/types/presentation";
import { PLANT_SPECIES } from "$lib/features/companion-widget/model/plants";

export function isPlantSpecies(value: string): value is PlantSpecies {
  return PLANT_SPECIES.some((species) => species === value);
}

// Inspected 2304x896 atlases, 8 columns x 2 rows, row-major indices.
// Healthy: sprout 1, growing 4, bloom 7 (bonsai flowering 10), lush 10/11.
// Late cells depict decline, not additional growth. See spec 019 research.md.
const healthyFrames: Record<
  PlantSpecies,
  Record<GrowthStage, PlantFrameIndex>
> = {
  monstera: { SPROUTING: 1, GROWING: 4, BLOOMING: 7, FLOURISHING: 10 },
  sunflower: { SPROUTING: 1, GROWING: 4, BLOOMING: 7, FLOURISHING: 11 },
  bonsai: { SPROUTING: 1, GROWING: 4, BLOOMING: 10, FLOURISHING: 11 },
  jasmine: { SPROUTING: 1, GROWING: 4, BLOOMING: 7, FLOURISHING: 11 },
  lavender: { SPROUTING: 1, GROWING: 4, BLOOMING: 7, FLOURISHING: 11 },
};
export function getPlantFrame(
  species: PlantSpecies,
  stage: GrowthStage,
  vitality: number,
): PlantFrameIndex {
  // Atlases have no stressed juvenile variants; vitality uses the available decline cells.
  if (vitality <= 0) return 15;
  if (vitality < 25) return 14;
  if (vitality < 50) return 13;
  if (vitality < 75) return 12;
  return healthyFrames[species][stage];
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
    frameIndex: getPlantFrame(
      plant.species,
      garden.growth_stage,
      garden.vitality,
    ),
  };
}
