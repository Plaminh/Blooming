import type { PlantId, PlantPresentation, UserSessionState, GardenSelectionState } from '../types';

export const MONSTERA: PlantPresentation = {
  id: 'monstera',
  name: 'Monstera',
  description: [
    'A bold and beautiful plant with iconic leaves.',
    'Brings a sense of calm and adventure to your space.'
  ],
  species: 'monstera',
  unlockCost: 120
};

export const INITIAL_USER_SESSION: UserSessionState = {
  currencyBalance: 124,
  unlockedPlants: new Set<PlantId>()
};

export const INITIAL_GARDEN_STATE: GardenSelectionState = {
  plants: [MONSTERA],
  currentIndex: 0,
  session: INITIAL_USER_SESSION
};
