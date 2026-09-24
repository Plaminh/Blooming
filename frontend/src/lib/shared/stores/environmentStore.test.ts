import { get } from 'svelte/store';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { environmentStore } from './environmentStore';
import { api } from '$lib/api';
import { WeatherCondition, WeatherStatus } from '$lib/types/weather';

vi.mock('$lib/api', () => ({ api: { get: vi.fn(), put: vi.fn() } }));
vi.mock('$lib/platform/desktopWindow', () => ({
  desktop: { onSettingsUpdated: vi.fn(async () => () => {}), settingsUpdated: vi.fn(async () => {}) },
}));

const settings = {
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
  weather_enabled: true,
  weather_lat: 51.51,
  scene_season: 'AUTO',
  weather_animation_enabled: true,
  widget_visibility: true,
};
const rain = { condition: WeatherCondition.RAIN, status: WeatherStatus.OK, updated_at: '2026-09-19T10:00:00Z' };
const flush = async () => { await Promise.resolve(); await Promise.resolve(); await Promise.resolve(); };

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date('2026-09-19T10:00:00Z'));
  environmentStore.resetForTests();
  vi.clearAllMocks();
  vi.mocked(api.get).mockImplementation(async (path: string) => path === '/me/settings' ? settings : rain);
  vi.mocked(api.put).mockResolvedValue({});
});
afterEach(() => { environmentStore.resetForTests(); vi.useRealTimers(); });

describe('environmentStore', () => {
  it('initializes once for two owners, polls every fifteen minutes and stops after the last release', async () => {
    const releaseOne = environmentStore.init();
    const releaseTwo = environmentStore.init();
    await flush();
    expect(api.get).toHaveBeenCalledTimes(2);
    expect(get(environmentStore).weatherCondition).toBe(WeatherCondition.RAIN);
    releaseOne();
    await vi.advanceTimersByTimeAsync(15 * 60 * 1000);
    expect(api.get).toHaveBeenCalledTimes(4);
    releaseTwo();
    await vi.advanceTimersByTimeAsync(15 * 60 * 1000);
    expect(api.get).toHaveBeenCalledTimes(4);
  });

  it('throttles focus but responds to settings updates', async () => {
    const release = environmentStore.init();
    await flush();
    window.dispatchEvent(new Event('focus'));
    await flush();
    expect(api.get).toHaveBeenCalledTimes(2);
    await vi.advanceTimersByTimeAsync(5 * 60 * 1000);
    window.dispatchEvent(new Event('focus'));
    await flush();
    expect(api.get).toHaveBeenCalledTimes(4);
    window.dispatchEvent(new Event('blooming:settings-updated'));
    await flush();
    expect(api.get).toHaveBeenCalledTimes(6);
    release();
  });

  it('shares an in-flight promise and retains rain after a transport failure', async () => {
    let finish!: (value: unknown) => void;
    vi.mocked(api.get).mockImplementationOnce(async () => settings)
      .mockImplementationOnce(() => new Promise((resolve) => { finish = resolve; }));
    const first = environmentStore.refresh();
    await flush();
    const second = environmentStore.refresh();
    expect(second).toBe(first);
    finish(rain);
    await first;
    expect(get(environmentStore).weatherCondition).toBe(WeatherCondition.RAIN);
    vi.mocked(api.get).mockRejectedValueOnce(new Error('offline'));
    await environmentStore.refresh();
    expect(get(environmentStore).weatherCondition).toBe(WeatherCondition.RAIN);
    expect(get(environmentStore).weatherStatus).toBe(WeatherStatus.STALE);
  });

  it('uses CLEAR visually for explicit unavailable and disabled states', async () => {
    vi.mocked(api.get).mockImplementation(async (path: string) => path === '/me/settings' ? settings
      : { condition: WeatherCondition.RAIN, status: WeatherStatus.UNAVAILABLE, updated_at: null });
    await environmentStore.refresh();
    expect(get(environmentStore).weatherCondition).toBe(WeatherCondition.CLEAR);
    expect(get(environmentStore).weatherStatus).toBe(WeatherStatus.UNAVAILABLE);
    vi.mocked(api.get).mockResolvedValueOnce({ ...settings, weather_enabled: false });
    await environmentStore.refresh();
    expect(get(environmentStore).weatherStatus).toBe(WeatherStatus.DISABLED);
  });

  it('rejects a response from an older request generation', async () => {
    let finishOld!: (value: unknown) => void;
    vi.mocked(api.get).mockImplementationOnce(async () => settings)
      .mockImplementationOnce(() => new Promise((resolve) => { finishOld = resolve; }));
    const oldRequest = environmentStore.refresh();
    await flush();
    environmentStore.resetForTests();
    vi.mocked(api.get).mockImplementation(async (path: string) => path === '/me/settings' ? settings
      : { condition: WeatherCondition.CLOUDY, status: WeatherStatus.OK, updated_at: 'new' });
    await environmentStore.refresh();
    finishOld(rain);
    await oldRequest;
    expect(get(environmentStore).weatherCondition).toBe(WeatherCondition.CLOUDY);
  });

  it('writes a changed timezone, keeps it effective if persistence fails, and retries later without duplicate writes', async () => {
    const different = { ...settings, timezone: 'Pacific/Honolulu' };
    vi.mocked(api.get).mockImplementation(async (path: string) => path === '/me/settings' ? different : rain);
    const release = environmentStore.init();
    
    // First fails
    vi.mocked(api.put).mockRejectedValueOnce(new Error('offline'));
    await environmentStore.refresh();
    await flush();
    expect(api.put).toHaveBeenCalledTimes(1);
    expect(get(environmentStore).effectiveTimezone).toBe(settings.timezone);
    
    // Next refresh retries, let it block to test duplicates
    let finishPut!: (value: unknown) => void;
    vi.mocked(api.put).mockImplementationOnce(() => new Promise((resolve) => { finishPut = resolve; }));
    
    const retry = environmentStore.refresh();
    await flush();
    
    // Only one new put in flight
    expect(api.put).toHaveBeenCalledTimes(2);
    
    finishPut({});
    await retry;
    await flush();
    
    // Next refresh should NOT retry since it succeeded
    await environmentStore.refresh();
    expect(api.put).toHaveBeenCalledTimes(2);
    
    release();
  });

  it('queues exactly one follow-up refresh for settings updates during an active request', async () => {
    let finishSettings!: (value: unknown) => void;
    
    // First request blocks on settings
    vi.mocked(api.get).mockImplementationOnce(() => new Promise((resolve) => { finishSettings = resolve; }));
    
    const release = environmentStore.init();
    await flush();
    
    // Trigger settings update multiple times
    window.dispatchEvent(new Event('blooming:settings-updated'));
    window.dispatchEvent(new Event('blooming:settings-updated'));
    await flush();
    
    // Still waiting, no new requests yet
    expect(api.get).toHaveBeenCalledTimes(1);
    
    // Complete first request
    finishSettings(settings);
    await flush();
    await flush();
    
    // Follow-up request should have started (first weather + follow-up settings + follow-up weather = 3 more calls)
    expect(api.get).toHaveBeenCalledTimes(4);
    
    release();
  });

  it('uses the newest returned settings for the follow-up refresh', async () => {
    let finishFirstSettings!: (value: unknown) => void;
    
    // First request
    vi.mocked(api.get).mockImplementationOnce(() => new Promise((resolve) => { finishFirstSettings = resolve; }));
    
    const release = environmentStore.init();
    await flush();
    
    // Update settings
    window.dispatchEvent(new Event('blooming:settings-updated'));
    
    // Next request returns a new settings object
    const newSettings = { ...settings, weather_animation_enabled: false };
    vi.mocked(api.get).mockImplementation(async (path: string) => path === '/me/settings' ? newSettings : rain);
    
    finishFirstSettings(settings);
    await flush();
    await flush();
    
    expect(get(environmentStore).animationEnabled).toBe(false);
    release();
  });

  it('prevents stale queued work on release/reset', async () => {
    let finishFirstSettings!: (value: unknown) => void;
    vi.mocked(api.get).mockImplementationOnce(() => new Promise((resolve) => { finishFirstSettings = resolve; }));
    
    const firstRequest = environmentStore.refresh();
    await flush();
    
    // Trigger queue
    window.dispatchEvent(new Event('blooming:settings-updated'));
    
    // Reset store
    environmentStore.resetForTests();
    
    finishFirstSettings(settings);
    await firstRequest;
    await flush();
    
    // Should not have started follow-up refresh
    expect(api.get).toHaveBeenCalledTimes(1);
  });

  it('does not write timezone if saved and detected values already match', async () => {
    vi.mocked(api.get).mockImplementation(async (path: string) => path === '/me/settings' ? settings : rain);
    await environmentStore.refresh();
    await flush();
    expect(api.put).not.toHaveBeenCalled();
  });
});
