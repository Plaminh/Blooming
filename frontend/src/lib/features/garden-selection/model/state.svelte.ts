import { SvelteSet } from 'svelte/reactivity';
import type { PlantId, PlantPresentation, UserSessionState } from '../types';

export class GardenSelectionViewModel {
  plants: PlantPresentation[] = $state([]);
  currentIndex: number = $state(0);
  
  currencyBalance: number = $state(0);
  unlockedPlants: SvelteSet<PlantId> = $state(new SvelteSet<PlantId>());

  constructor(
    plants: PlantPresentation[],
    initialSession: UserSessionState
  ) {
    this.plants = plants;
    this.currencyBalance = initialSession.currencyBalance;
    this.unlockedPlants = new SvelteSet(initialSession.unlockedPlants);
  }

  get selectedPlant(): PlantPresentation | undefined {
    return this.plants[this.currentIndex];
  }

  get hasPrevious(): boolean {
    return this.currentIndex > 0;
  }

  get hasNext(): boolean {
    return this.currentIndex < this.plants.length - 1;
  }

  previous() {
    if (this.hasPrevious) {
      this.currentIndex--;
    }
  }

  next() {
    if (this.hasNext) {
      this.currentIndex++;
    }
  }

  get isSelectedPlantUnlocked(): boolean {
    if (!this.selectedPlant) return false;
    return this.unlockedPlants.has(this.selectedPlant.id);
  }

  get canUnlockSelectedPlant(): boolean {
    if (!this.selectedPlant) return false;
    if (this.isSelectedPlantUnlocked) return false;
    return this.currencyBalance >= this.selectedPlant.unlockCost;
  }

  unlockSelectedPlant() {
    if (this.canUnlockSelectedPlant && this.selectedPlant) {
      this.currencyBalance -= this.selectedPlant.unlockCost;
      this.unlockedPlants.add(this.selectedPlant.id);
    }
  }
}
