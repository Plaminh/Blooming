import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { api } from '$lib/api';
import type { UserSettingsResponse } from '$lib/api/types';
import { desktop } from '$lib/platform/desktopWindow';
import { deviceTimezone } from '$lib/shared/deviceLocation';
import { resolveSeason } from '$lib/shared/utils/season';
import { WeatherCondition, WeatherStatus, SceneSeason, type WeatherResponse } from '$lib/types/weather';

export interface EnvironmentState {
  weatherCondition: WeatherCondition;
  weatherStatus: WeatherStatus;
  sceneSeason: SceneSeason;
  effectiveTimezone: string;
  animationEnabled: boolean;
  widgetVisible: boolean;
  lastUpdated: string | null;
  isLoading: boolean;
  lastAttempt: number | null;
}

const initialState: EnvironmentState = {
  weatherCondition: WeatherCondition.CLEAR,
  weatherStatus: WeatherStatus.DISABLED,
  sceneSeason: SceneSeason.AUTO,
  effectiveTimezone: deviceTimezone(),
  animationEnabled: true,
  widgetVisible: true,
  lastUpdated: null,
  isLoading: false,
  lastAttempt: null,
};
const store = writable<EnvironmentState>(initialState);
let current = initialState;
store.subscribe((value) => { current = value; });
const set = (patch: Partial<EnvironmentState>) => store.update((state) => ({ ...state, ...patch }));
let owners = 0;
let interval: ReturnType<typeof setInterval> | null = null;
let unlistenDesktop: (() => void) | null = null;
let generation = 0;
let inFlight: Promise<void> | null = null;
let refreshQueued = false;
let timezoneWriteInFlight: string | null = null;
let lastSuccessfulTimezone: string | null = null;

async function syncTimezone(saved: string, detected: string): Promise<void> {
  if (saved === detected) {
    lastSuccessfulTimezone = detected;
    return;
  }
  if (lastSuccessfulTimezone === detected || timezoneWriteInFlight === detected) return;

  timezoneWriteInFlight = detected;
  try {
    await api.put('/me/settings', { timezone: detected });
    lastSuccessfulTimezone = detected;
    if (browser) window.dispatchEvent(new Event('blooming:settings-updated'));
    await desktop.settingsUpdated();
  } catch {
    // Keep the device timezone effective even if persistence is unavailable.
  } finally {
    if (timezoneWriteInFlight === detected) {
      timezoneWriteInFlight = null;
    }
  }
}

async function performRefresh(id: number): Promise<void> {
  set({ isLoading: true, lastAttempt: Date.now() });
  try {
    const settings = await api.get('/me/settings') as UserSettingsResponse;
    if (id !== generation) return;
    const timezone = deviceTimezone();
    set({
      effectiveTimezone: timezone,
      sceneSeason: resolveSeason(settings.scene_season, new Date().getMonth(), settings.weather_lat),
      animationEnabled: settings.weather_animation_enabled !== false,
      widgetVisible: settings.widget_visibility !== false,
    });
    void syncTimezone(settings.timezone, timezone);
    if (!settings.weather_enabled) {
      set({ weatherCondition: WeatherCondition.CLEAR, weatherStatus: WeatherStatus.DISABLED, lastUpdated: null });
      return;
    }
    const response = await api.get('/weather/current') as WeatherResponse;
    if (id !== generation) return;
    if (response.status === WeatherStatus.OK || response.status === WeatherStatus.STALE) {
      set({ weatherCondition: response.condition, weatherStatus: response.status, lastUpdated: response.updated_at });
    } else {
      set({ weatherCondition: WeatherCondition.CLEAR, weatherStatus: response.status, lastUpdated: null });
    }
  } catch {
    if (id === generation) {
      set({ weatherStatus: current.lastUpdated ? WeatherStatus.STALE : WeatherStatus.UNAVAILABLE });
    }
  } finally {
    if (id === generation) set({ isLoading: false });
  }
}

function refresh(): Promise<void> {
  if (inFlight) return inFlight;
  refreshQueued = false;
  const id = ++generation;
  const request = performRefresh(id);
  inFlight = request;
  void request.finally(() => { 
    if (inFlight === request) {
      inFlight = null;
      if (refreshQueued && owners > 0) {
        void refresh();
      }
    }
  });
  return request;
}

function onFocus() {
  if (current.lastAttempt === null || Date.now() - current.lastAttempt >= 5 * 60 * 1000) void refresh();
}
function onSettingsUpdated() {
  if (inFlight) {
    refreshQueued = true;
  } else {
    void refresh();
  }
}

function init(): () => void {
  if (!browser) return () => {};
  owners += 1;
  if (owners === 1) {
    void refresh();
    interval = setInterval(() => void refresh(), 15 * 60 * 1000);
    window.addEventListener('focus', onFocus);
    window.addEventListener('blooming:settings-updated', onSettingsUpdated);
    void desktop.onSettingsUpdated(onSettingsUpdated).then((off) => {
      if (owners === 0) off();
      else unlistenDesktop = off;
    }).catch(() => {});
  }
  let released = false;
  return () => {
    if (released) return;
    released = true;
    owners -= 1;
    if (owners > 0) return;
    if (interval) clearInterval(interval);
    interval = null;
    window.removeEventListener('focus', onFocus);
    window.removeEventListener('blooming:settings-updated', onSettingsUpdated);
    unlistenDesktop?.();
    unlistenDesktop = null;
  };
}

export const environmentStore = {
  subscribe: store.subscribe,
  init,
  refresh,
  resetForTests: () => {
    if (interval) clearInterval(interval);
    interval = null;
    if (browser) {
      window.removeEventListener('focus', onFocus);
      window.removeEventListener('blooming:settings-updated', onSettingsUpdated);
    }
    unlistenDesktop?.();
    unlistenDesktop = null;
    owners = 0;
    generation += 1;
    inFlight = null;
    refreshQueued = false;
    timezoneWriteInFlight = null;
    lastSuccessfulTimezone = null;
    store.set(initialState);
  },
};
