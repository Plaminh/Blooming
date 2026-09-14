export type PlantId = 'monstera' | 'sunflower' | 'bonsai' | 'jasmine' | 'lavender';
export type PlantSpecies = PlantId;

export interface PlantPresentation {
  id: PlantId;
  name: string;
  description: string[];
  species: PlantSpecies;
  unlockCost: number;
}

export interface UserSessionState {
  currencyBalance: number;
  unlockedPlants: Set<PlantId>;
}

export interface GardenSelectionState {
  plants: PlantPresentation[];
  currentIndex: number;
  session: UserSessionState;
}
