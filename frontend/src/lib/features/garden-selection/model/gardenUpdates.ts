import { writable } from 'svelte/store';

export const gardenUpdates = writable(0);

export function notifyGardenUpdated() {
  gardenUpdates.update((revision) => revision + 1);
}
