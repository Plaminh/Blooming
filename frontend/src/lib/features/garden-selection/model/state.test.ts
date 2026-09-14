import { describe, it, expect, beforeEach } from 'vitest';
import { GardenSelectionViewModel } from './state.svelte';
import { INITIAL_GARDEN_STATE, MONSTERA } from './fixtures';

describe('GardenSelectionViewModel', () => {
  let vm: GardenSelectionViewModel;

  beforeEach(() => {
    vm = new GardenSelectionViewModel(INITIAL_GARDEN_STATE.plants, INITIAL_GARDEN_STATE.session);
  });

  it('should initialize with correct initial state', () => {
    expect(vm.selectedPlant).toEqual(MONSTERA);
    expect(vm.currencyBalance).toBe(124);
    expect(vm.selectedPlant?.unlockCost).toBe(120);
    expect(vm.isSelectedPlantUnlocked).toBe(false);
  });

  it('should allow unlocking when balance is sufficient', () => {
    expect(vm.canUnlockSelectedPlant).toBe(true);
    vm.unlockSelectedPlant();
    expect(vm.currencyBalance).toBe(4);
    expect(vm.isSelectedPlantUnlocked).toBe(true);
  });

  it('should prevent unlocking when already unlocked', () => {
    vm.unlockSelectedPlant();
    expect(vm.currencyBalance).toBe(4);
    expect(vm.isSelectedPlantUnlocked).toBe(true);
    expect(vm.canUnlockSelectedPlant).toBe(false);

    // Try to unlock again
    vm.unlockSelectedPlant();
    expect(vm.currencyBalance).toBe(4); // Balance should not decrease
  });

  it('should prevent unlocking when balance is insufficient', () => {
    // Manually set balance too low
    vm.currencyBalance = 100;
    expect(vm.canUnlockSelectedPlant).toBe(false);

    vm.unlockSelectedPlant();
    expect(vm.currencyBalance).toBe(100);
    expect(vm.isSelectedPlantUnlocked).toBe(false);
  });

  it('should support exact-cost balance', () => {
    vm.currencyBalance = 120;
    expect(vm.canUnlockSelectedPlant).toBe(true);
    
    vm.unlockSelectedPlant();
    expect(vm.currencyBalance).toBe(0);
    expect(vm.isSelectedPlantUnlocked).toBe(true);
  });

  describe('Carousel Navigation', () => {
    beforeEach(() => {
      // Setup a multi-plant mock
      vm = new GardenSelectionViewModel(
        [
          MONSTERA,
          { ...MONSTERA, id: 'sunflower', name: 'Sunflower' },
          { ...MONSTERA, id: 'bonsai', name: 'Bonsai' }
        ],
        INITIAL_GARDEN_STATE.session
      );
    });

    it('should navigate through plants', () => {
      expect(vm.currentIndex).toBe(0);
      expect(vm.selectedPlant?.id).toBe('monstera');
      expect(vm.hasPrevious).toBe(false);
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
      expect(vm.hasNext).toBe(false);
      
      // Should respect bounds
      vm.next();
      expect(vm.currentIndex).toBe(2);

      vm.previous();
      expect(vm.currentIndex).toBe(1);
    });

    it('should preserve unlock state during navigation', () => {
      vm.unlockSelectedPlant();
      expect(vm.isSelectedPlantUnlocked).toBe(true);

      vm.next();
      expect(vm.isSelectedPlantUnlocked).toBe(false);

      vm.previous();
      expect(vm.isSelectedPlantUnlocked).toBe(true);
    });
  });
});
