import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { GardenSelectionViewModel } from './state.svelte';
import { api } from '$lib/api';

vi.mock('$lib/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn()
  },
  APIError: class extends Error {
    status: number;
    constructor(status: number, message: string) {
      super(message);
      this.status = status;
      this.name = 'APIError';
    }
  }
}));

describe('GardenSelectionViewModel', () => {
  let vm: GardenSelectionViewModel;
  
  const mockGardenData = {
    water_balance: 0,
    leaves_balance: 124,
    vitality: 100,
    growth_stage: 'SPROUTING',
    selected_plant_id: 'monstera',
    catalog: [
      {
        id: 'monstera',
        name: 'Monstera',
        description: 'A bold and beautiful plant with iconic leaves.',
        species: 'monstera',
        unlock_cost: 120,
        is_unlocked: false,
        is_selected: true
      }
    ]
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (api.get as any).mockResolvedValue(mockGardenData);
    vm = new GardenSelectionViewModel();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should initialize with correct initial state via API', async () => {
    // wait for loadState to complete
    await vi.waitFor(() => { expect(vm.loading).toBe(false); });

    expect(api.get).toHaveBeenCalledWith('/garden');
    expect(vm.selectedPlant?.id).toBe('monstera');
    expect(vm.leavesBalance).toBe(124);
    expect(vm.selectedPlant?.unlockCost).toBe(120);
    expect(vm.isSelectedPlantUnlocked).toBe(false);
    expect(vm.activePlantPresentation).toEqual({ species: 'monstera', frameIndex: 0, scale: 1 });
  });

  it('maps a dormant sprouting Monstera to the fourth vitality column', async () => {
    (api.get as any).mockResolvedValue({ ...mockGardenData, vitality: 0 });
    vm = new GardenSelectionViewModel();
    await vi.waitFor(() => expect(vm.loading).toBe(false));
    expect(vm.activePlantPresentation).toEqual({ species: 'monstera', frameIndex: 3, scale: 1 });
  });

  it('plays watering only after API success and refreshes when it finishes', async () => {
    const waterable = { ...mockGardenData, water_balance: 2, catalog: [{ ...mockGardenData.catalog[0], is_unlocked: true }] };
    (api.get as any).mockResolvedValue(waterable);
    vm = new GardenSelectionViewModel();
    await vi.waitFor(() => expect(vm.loading).toBe(false));
    vi.mocked(api.get).mockClear();
    (api.post as any).mockResolvedValue({ water_balance: 1, vitality: 100, last_watered_at: "now" });

    await vm.waterSelectedPlant(true);
    expect(api.post).toHaveBeenCalledTimes(1);
    expect(vm.isWatering).toBe(true);
    expect(vm.isPending).toBe(true);
    await vm.finishWatering();
    expect(api.get).toHaveBeenCalledTimes(1);
    expect(vm.isWatering).toBe(false);
    expect(vm.isPending).toBe(false);
  });

  it('does not animate on water failure', async () => {
    const waterable = { ...mockGardenData, water_balance: 1, catalog: [{ ...mockGardenData.catalog[0], is_unlocked: true }] };
    (api.get as any).mockResolvedValue(waterable);
    vm = new GardenSelectionViewModel();
    await vi.waitFor(() => expect(vm.loading).toBe(false));
    (api.post as any).mockRejectedValue(new Error('offline'));
    await vm.waterSelectedPlant(true);
    expect(vm.isWatering).toBe(false);
    expect(vm.vitality).toBe(100);
  });

  it('blocks rapid repeat watering while pending or animating', async () => {
    const waterable = { ...mockGardenData, water_balance: 2, catalog: [{ ...mockGardenData.catalog[0], is_unlocked: true }] };
    (api.get as any).mockResolvedValue(waterable);
    vm = new GardenSelectionViewModel();
    await vi.waitFor(() => expect(vm.loading).toBe(false));
    (api.post as any).mockResolvedValue({ water_balance: 1, vitality: 100, last_watered_at: "now" });
    await vm.waterSelectedPlant(true);
    await vm.waterSelectedPlant(true);
    expect(api.post).toHaveBeenCalledTimes(1);
  });

  it('skips animation but still refreshes when animation is disabled', async () => {
    const waterable = { ...mockGardenData, water_balance: 1, catalog: [{ ...mockGardenData.catalog[0], is_unlocked: true }] };
    (api.get as any).mockResolvedValue(waterable);
    vm = new GardenSelectionViewModel();
    await vi.waitFor(() => expect(vm.loading).toBe(false));
    vi.mocked(api.get).mockClear();
    (api.post as any).mockResolvedValue({ water_balance: 0, vitality: 100, last_watered_at: "now" });
    await vm.waterSelectedPlant(false);
    expect(vm.isWatering).toBe(false);
    expect(api.get).toHaveBeenCalledTimes(1);
  });

  it('should allow unlocking when balance is sufficient', async () => {
    await vi.waitFor(() => { expect(vm.loading).toBe(false); });

    expect(vm.canUnlockSelectedPlant).toBe(true);

    const unlockedData = JSON.parse(JSON.stringify(mockGardenData));
    unlockedData.leaves_balance = 4;
    unlockedData.catalog[0].is_unlocked = true;
    (api.post as any).mockResolvedValue(unlockedData);

    await vm.unlockSelectedPlant();

    expect(api.post).toHaveBeenCalledWith('/garden/plants/monstera/unlock');
    expect(vm.leavesBalance).toBe(4);
    expect(vm.isSelectedPlantUnlocked).toBe(true);
  });

  it('should prevent unlocking when already unlocked', async () => {
    const unlockedData = JSON.parse(JSON.stringify(mockGardenData));
    unlockedData.leaves_balance = 4;
    unlockedData.catalog[0].is_unlocked = true;
    (api.get as any).mockResolvedValue(unlockedData);
    
    vm = new GardenSelectionViewModel();
    await vi.waitFor(() => { expect(vm.loading).toBe(false); });

    expect(vm.isSelectedPlantUnlocked).toBe(true);
    expect(vm.canUnlockSelectedPlant).toBe(false);

    await vm.unlockSelectedPlant();
    // Post should not be called
    expect(api.post).not.toHaveBeenCalled();
  });

  it('should support exact-cost balance', async () => {
    const exactBalanceData = JSON.parse(JSON.stringify(mockGardenData));
    exactBalanceData.leaves_balance = 120;
    (api.get as any).mockResolvedValue(exactBalanceData);
    
    vm = new GardenSelectionViewModel();
    await vi.waitFor(() => { expect(vm.loading).toBe(false); });


    expect(vm.canUnlockSelectedPlant).toBe(true);
    
    const unlockedData = JSON.parse(JSON.stringify(exactBalanceData));
    unlockedData.leaves_balance = 0;
    unlockedData.catalog[0].is_unlocked = true;
    (api.post as any).mockResolvedValue(unlockedData);
    await vm.unlockSelectedPlant();
    expect(vm.leavesBalance).toBe(0);
    expect(vm.isSelectedPlantUnlocked).toBe(true);
  });

  describe('Carousel Navigation', () => {
    beforeEach(async () => {
      const multiData = {
        ...mockGardenData,
        catalog: [
          mockGardenData.catalog[0],
          { ...mockGardenData.catalog[0], id: 'sunflower', name: 'Sunflower', species: 'sunflower', is_selected: false },
          { ...mockGardenData.catalog[0], id: 'bonsai', name: 'Bonsai', species: 'bonsai', is_selected: false }
        ]
      };
      (api.get as any).mockResolvedValue(multiData);
      vm = new GardenSelectionViewModel();
      await vi.waitFor(() => { expect(vm.loading).toBe(false); });
    });

    it('should navigate through plants', () => {
      expect(vm.currentIndex).toBe(0);
      expect(vm.selectedPlant?.id).toBe('monstera');
      expect(vm.hasPrevious).toBe(true);
      expect(vm.hasNext).toBe(true);

      vm.next();
      expect(vm.currentIndex).toBe(1);
      expect(vm.selectedPlant?.id).toBe('sunflower');
      expect(vm.hasPrevious).toBe(true);
      expect(vm.hasNext).toBe(true);

      vm.next();
      expect(vm.currentIndex).toBe(2);
      expect(vm.selectedPlant?.id).toBe('bonsai');
      expect(vm.hasPrevious).toBe(true);
      expect(vm.hasNext).toBe(true);
      
      // Navigation wraps so both arrows remain usable.
      vm.next();
      expect(vm.currentIndex).toBe(0);

      vm.previous();
      expect(vm.currentIndex).toBe(2);

    });
  });

  it('should prevent unlocking when balance is insufficient', async () => {
    const insufficientData = JSON.parse(JSON.stringify(mockGardenData));
    insufficientData.leaves_balance = 50; // Cost is 120
    (api.get as any).mockResolvedValue(insufficientData);
    
    vm = new GardenSelectionViewModel();
    await vi.waitFor(() => { expect(vm.loading).toBe(false); });

    expect(vm.canUnlockSelectedPlant).toBe(false);

    await vm.unlockSelectedPlant();
    expect(api.post).not.toHaveBeenCalled();
  });
});
