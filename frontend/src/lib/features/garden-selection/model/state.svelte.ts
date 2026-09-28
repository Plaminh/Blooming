import type { GardenState, GrowthStage } from "$lib/api/types";
import {
  isPlantSpecies,
  selectedPlantPresentation,
} from '$lib/shared/sprites/spriteMapper';
import type { ActivePlantPresentation } from '$lib/shared/sprites/types';
import { PLANT_SPECIES } from '$lib/shared/sprites/plants';
import { desktop } from "$lib/platform/desktopWindow";
import { SvelteSet } from "svelte/reactivity";
import type { PlantPresentation } from "../types";
import { api, APIError } from "$lib/api";
import { notifyGardenUpdated } from "./gardenUpdates";

export class GardenSelectionViewModel {
  plants: PlantPresentation[] = $state([]);
  currentIndex: number = $state(0);

  waterBalance: number = $state(0);
  leavesBalance: number = $state(0);
  unlockedPlants: SvelteSet<string> = $state(new SvelteSet<string>());
  vitality: number = $state(100);

  loading: boolean = $state(true);
  error: string | null = $state(null);
  syncWarning: string | null = $state(null);
  isPending = $state(false);
  isWatering = $state(false);

  activePlantId: string | null = $state(null);
  activePlantPresentation: ActivePlantPresentation | null = $state(null);
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
    const viewedPlantId = this.selectedPlant?.id;
    this.waterBalance = data.water_balance;
    this.leavesBalance = data.leaves_balance;
    this.vitality = data.vitality;
    this.activePlantId = data.selected_plant_id;
    this.activePlantPresentation = selectedPlantPresentation(data);
    this.growthStage = data.growth_stage;

    const newPlants: PlantPresentation[] = [];
    let activeIdx = 0;
    this.unlockedPlants.clear();

    if (Array.isArray(data.catalog)) {
      const catalog = [...data.catalog].sort(
        (a, b) => PLANT_SPECIES.indexOf(a.species as typeof PLANT_SPECIES[number]) - PLANT_SPECIES.indexOf(b.species as typeof PLANT_SPECIES[number]),
      );
      for (const p of catalog) {
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
    const viewedIndex = newPlants.findIndex((plant) => plant.id === viewedPlantId);
    this.currentIndex = viewedIndex >= 0 ? viewedIndex : activeIdx;
  }

  get selectedPlant(): PlantPresentation | undefined {
    return this.plants[this.currentIndex];
  }

  get hasPrevious(): boolean {
    return this.plants.length > 1;
  }

  get hasNext(): boolean {
    return this.plants.length > 1;
  }

  previous() {
    if (this.hasPrevious) this.currentIndex = (this.currentIndex - 1 + this.plants.length) % this.plants.length;
  }

  next() {
    if (this.hasNext) this.currentIndex = (this.currentIndex + 1) % this.plants.length;
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
        notifyGardenUpdated();
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
        notifyGardenUpdated();
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

  wateringOperationKey: string | null = null;

  get canWaterSelectedPlant(): boolean {
    return this.selectedPlant?.id === this.activePlantId && this.waterBalance >= 1 && !this.isPending;
  }

  async waterSelectedPlant(animate = true): Promise<boolean> {
    if (!this.canWaterSelectedPlant) return false;
    this.isPending = true;
    this.syncWarning = null;
    if (!this.wateringOperationKey) {
      this.wateringOperationKey = crypto.randomUUID();
    }
    try {
      await api.post("/garden/water", { operation_key: this.wateringOperationKey });
      this.error = null;
      if (animate) {
        this.isWatering = true;
      } else {
        await this.finishWatering();
      }
      return true;
    } catch (e: unknown) {
      if (e instanceof APIError && (e.status === 409 || e.status === 400)) {
        this.error = e.message || "Not enough water or conflict";
      } else if (e instanceof Error) {
        this.error = e.message || "Failed to water plant";
      } else {
        this.error = "Failed to water plant";
      }
      this.isPending = false;
      return false;
    }
  }

  async finishWatering() {
    if (!this.isPending) return;
    this.isWatering = false;
    this.wateringOperationKey = null;
    await this.loadState();
    notifyGardenUpdated();
    await this.syncWidget("Plant watered, but widget sync failed.");
    this.isPending = false;
  }

  private async syncWidget(message: string) {
    try {
      await desktop.scheduleUpdated();
    } catch {
      this.syncWarning = message;
    }
  }
}
