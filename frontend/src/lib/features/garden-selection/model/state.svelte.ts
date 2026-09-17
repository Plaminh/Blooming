import type {
  GardenState,
  GrowthStage,
  WaterPlantResponse,
} from "$lib/api/types";
import {
  getPlantFrame,
  isPlantSpecies,
} from "$lib/features/garden/utils/spriteMapper";
import { desktop } from "$lib/platform/desktopWindow";
import { SvelteSet } from "svelte/reactivity";
import type { PlantPresentation } from "../types";
import { api, APIError } from "$lib/api";

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
  syncWarning: string | null = $state(null);
  isPending = $state(false);

  activePlantId: string | null = $state(null);
  growthStage: GrowthStage = $state("SPROUTING");

  constructor() {
    this.loadState();
  }

  async loadState() {
    this.loading = true;
    this.error = null;
    try {
      const data: GardenState = await api.get("/garden");
      this.updateFromData(data);
    } catch (e: unknown) {
      if (e instanceof Error) {
        this.error = e.message || "Failed to load garden state";
      } else {
        this.error = "Failed to load garden state";
      }
    } finally {
      this.loading = false;
    }
  }

  updateFromData(data: GardenState) {
    this.waterBalance = data.water_balance;
    this.leavesBalance = data.leaves_balance;
    this.vitality = data.vitality;
    this.activePlantId = data.selected_plant_id;
    this.growthStage = data.growth_stage;

    const newPlants: PlantPresentation[] = [];
    let activeIdx = 0;
    this.unlockedPlants.clear();

    if (Array.isArray(data.catalog)) {
      for (let i = 0; i < data.catalog.length; i++) {
        const p = data.catalog[i];
        if (!isPlantSpecies(p.species)) continue;
        if (p.is_unlocked) {
          this.unlockedPlants.add(p.id);
        }
        if (p.is_selected) {
          activeIdx = newPlants.length;
        }
        newPlants.push({
          id: p.id,
          name: p.name,
          description: [p.description],
          species: p.species,
          unlockCost: p.unlock_cost,
        });
      }
    }

    this.plants = newPlants;
    if (this.activePlantId && newPlants.length > 0) {
      this.currentIndex = activeIdx;
    }
  }

  get selectedPlant(): PlantPresentation | undefined {
    return this.plants[this.currentIndex];
  }

  get selectedFrame() {
    return this.selectedPlant
      ? getPlantFrame(
          this.selectedPlant.species,
          this.growthStage,
          this.vitality,
        )
      : undefined;
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
    if (this.isPending) return;
    if (this.canUnlockSelectedPlant && this.selectedPlant) {
      this.isPending = true;
      this.syncWarning = null;
      try {
        const data: GardenState = await api.post(
          `/garden/plants/${this.selectedPlant.id}/unlock`,
        );
        this.updateFromData(data);
        this.error = null;
        await this.syncWidget("Plant unlocked, but widget sync failed.");
      } catch (e: unknown) {
        if (e instanceof APIError && (e.status === 409 || e.status === 400)) {
          this.error = e.message || "Insufficient currency or conflict";
        } else if (e instanceof Error) {
          this.error = e.message || "Failed to unlock plant";
        } else {
          this.error = "Failed to unlock plant";
        }
      } finally {
        this.isPending = false;
      }
    }
  }

  async selectCurrentPlant() {
    if (this.isPending) return;
    if (this.isSelectedPlantUnlocked && this.selectedPlant) {
      this.isPending = true;
      this.syncWarning = null;
      try {
        const data: GardenState = await api.post(
          `/garden/plants/${this.selectedPlant.id}/select`,
        );
        this.updateFromData(data);
        this.error = null;
        await this.syncWidget("Plant selected, but widget sync failed.");
      } catch (e: unknown) {
        if (e instanceof Error) {
          this.error = e.message || "Failed to select plant";
        } else {
          this.error = "Failed to select plant";
        }
      } finally {
        this.isPending = false;
      }
    }
  }

  async waterSelectedPlant() {
    if (this.isPending) return;
    if (this.waterBalance >= 1) {
      this.isPending = true;
      this.syncWarning = null;
      try {
        const data: WaterPlantResponse = await api.post(`/garden/water`);
        this.waterBalance = data.water_balance;
        this.vitality = data.vitality;
        this.lastWateredAt = data.last_watered_at;
        this.error = null;
        await this.syncWidget("Plant watered, but widget sync failed.");
      } catch (e: unknown) {
        if (e instanceof APIError && (e.status === 409 || e.status === 400)) {
          this.error = e.message || "Not enough water or conflict";
        } else if (e instanceof Error) {
          this.error = e.message || "Failed to water plant";
        } else {
          this.error = "Failed to water plant";
        }
      } finally {
        this.isPending = false;
      }
    }
  }

  private async syncWidget(message: string) {
    try {
      await desktop.scheduleUpdated();
    } catch {
      this.syncWarning = message;
    }
  }
}
