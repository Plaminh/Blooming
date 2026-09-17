import { SvelteSet } from 'svelte/reactivity';
import type { PlantId, PlantPresentation } from '../types';
import { api } from '$lib/api';

export class GardenSelectionViewModel {
  plants: PlantPresentation[] = $state([]);
  currentIndex: number = $state(0);
  
  waterBalance: number = $state(0);
  leavesBalance: number = $state(0);
  unlockedPlants: SvelteSet<string> = $state(new SvelteSet<string>());
  vitality: number = $state(100);
  lastWateredAt: string | null = $state(null);
  
  loading: boolean = $state(true);
  error: string | null = $state(null);

  activePlantId: string | null = $state(null);

  constructor() {
    this.loadState();
  }

  async loadState() {
    this.loading = true;
    this.error = null;
    try {
      const data = await api.get('/api/garden');
      this.updateFromData(data);
    } catch (e: any) {
      this.error = e.message || 'Failed to load garden state';
    } finally {
      this.loading = false;
    }
  }

  updateFromData(data: any) {
    this.waterBalance = data.water_balance;
    this.leavesBalance = data.leaves_balance;
    this.vitality = data.vitality;
    this.activePlantId = data.selected_plant_id;
    
    const newPlants = [];
    let activeIdx = 0;
    this.unlockedPlants.clear();
    
    for (let i = 0; i < data.catalog.length; i++) {
      const p = data.catalog[i];
      if (p.is_unlocked) {
        this.unlockedPlants.add(p.id);
      }
      if (p.is_selected) {
        activeIdx = i;
      }
      newPlants.push({
        id: p.id as PlantId,
        name: p.name,
        description: [p.description],
        species: p.species as any,
        unlockCost: p.unlock_cost
      });
    }
    
    this.plants = newPlants;
    if (this.activePlantId) {
       this.currentIndex = activeIdx;
    }
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
    return this.leavesBalance >= this.selectedPlant.unlockCost;
  }

  async unlockSelectedPlant() {
    if (this.canUnlockSelectedPlant && this.selectedPlant) {
      try {
        const data = await api.post(`/api/garden/plants/${this.selectedPlant.id}/unlock`);
        this.updateFromData(data);
      } catch (e: any) {
        this.error = e.message || 'Failed to unlock plant';
      }
    }
  }

  async selectCurrentPlant() {
    if (this.isSelectedPlantUnlocked && this.selectedPlant) {
      try {
        const data = await api.post(`/api/garden/plants/${this.selectedPlant.id}/select`);
        this.updateFromData(data);
      } catch (e: any) {
        this.error = e.message || 'Failed to select plant';
      }
    }
  }

  async waterSelectedPlant() {
    if (this.waterBalance >= 1) {
      try {
        const data = await api.post(`/api/garden/water`);
        this.waterBalance = data.water_balance;
        this.vitality = data.vitality;
        this.lastWateredAt = data.last_watered_at;
      } catch (e: any) {
        this.error = e.message || 'Failed to water plant';
      }
    }
  }
}
