import { writable, type Writable } from 'svelte/store';

export interface SyncFreshness {
  running: boolean;
  lastSyncedAt: number | null;
  error: string | null;
}

export interface ResyncDependencies {
  fetchSession(): Promise<unknown>;
  fetchReminders(): Promise<unknown>;
  refreshPlant(): Promise<unknown>;
}

export function createResync(dependencies: ResyncDependencies) {
  const freshness: Writable<SyncFreshness> = writable({ running: false, lastSyncedAt: null, error: null });
  let inFlight: Promise<void> | null = null;

  function resync(): Promise<void> {
    if (inFlight) return inFlight;
    freshness.update(value => ({ ...value, running: true, error: null }));
    inFlight = Promise.all([
      dependencies.fetchSession(),
      dependencies.fetchReminders(),
      dependencies.refreshPlant()
    ]).then(() => {
      freshness.set({ running: false, lastSyncedAt: Date.now(), error: null });
    }).catch((cause: unknown) => {
      freshness.update(value => ({
        ...value,
        running: false,
        error: cause instanceof Error ? cause.message : 'Synchronization failed.'
      }));
      throw cause;
    }).finally(() => {
      inFlight = null;
    });
    return inFlight;
  }

  return { resync, freshness };
}

export async function synchronizeAuthenticatedStartup(
  authenticated: boolean,
  flush: () => Promise<unknown>,
  resync: () => Promise<unknown>,
) {
  if (!authenticated) return;
  await flush();
  await resync();
}
