export type PlantSpecies = "monstera" | "sunflower" | "bonsai" | "jasmine" | "lavender";

export type PlantFrameIndex = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15;

export interface ActivePlantPresentation {
  species: PlantSpecies;
  frameIndex: PlantFrameIndex;
  scale?: number;
}
