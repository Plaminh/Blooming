import { writable } from 'svelte/store';
import type { Snippet } from 'svelte';

export const overlayStore = writable<Snippet | undefined>(undefined);
