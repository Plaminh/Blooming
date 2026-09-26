import { render } from '@testing-library/svelte';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import WidgetSceneBackground from './WidgetSceneBackground.svelte';
import { DAYTIME_ASSETS, SEASON_ASSETS, WEATHER_ASSETS, RAIN_CONFIGS } from '../../model/environment';
import { writable } from 'svelte/store';

const { mockEnvStore, mockSettingsState } = vi.hoisted(() => {
  let value = {
    weatherCondition: 'CLEAR',
    sceneSeason: 'AUTO',
    effectiveTimezone: 'UTC',
    animationEnabled: true,
    widgetVisible: true,
  };
  const subs = new Set<Function>();
  
  return {
    mockEnvStore: {
      subscribe: (fn: Function) => {
        subs.add(fn);
        fn(value);
        return () => subs.delete(fn);
      },
      set: (newVal: any) => {
        value = newVal;
        subs.forEach(s => s(value));
      }
    },
    mockSettingsState: {
      savedSettings: {
        timezone: 'UTC',
        weatherAnimationEnabled: true
      }
    }
  };
});

vi.mock('$lib/shared/stores/environmentStore', () => ({
  environmentStore: mockEnvStore
}));

vi.mock('$lib/features/settings/model/SettingsState.svelte', () => ({
  getSettingsState: () => mockSettingsState
}));

describe('WidgetSceneBackground', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockEnvStore.set({ weatherCondition: 'CLEAR', sceneSeason: 'AUTO', effectiveTimezone: 'UTC', animationEnabled: true, widgetVisible: true });
    mockSettingsState.savedSettings.timezone = 'UTC';
    mockSettingsState.savedSettings.weatherAnimationEnabled = true;
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders correct daytime and season assets based on local time', () => {
    const fakeDate = new Date('2023-05-15T02:00:00Z'); // 9 AM in Ho Chi Minh City
    vi.setSystemTime(fakeDate);
    mockEnvStore.set({ weatherCondition: 'CLEAR', sceneSeason: 'AUTO', effectiveTimezone: 'Asia/Ho_Chi_Minh', animationEnabled: true, widgetVisible: true });

    const { container } = render(WidgetSceneBackground);

    const sky = container.querySelector('.sky') as HTMLImageElement;
    expect(sky.src).toContain(DAYTIME_ASSETS['MORNING']);

    const bushes = container.querySelector('.bushes') as HTMLImageElement;
    expect(bushes.src).toContain(SEASON_ASSETS['SPRING']);
  });
  
  it('respects scene season override from store', () => {
    const fakeDate = new Date('2023-05-15T02:00:00Z');
    vi.setSystemTime(fakeDate);
    mockEnvStore.set({ weatherCondition: 'CLEAR', sceneSeason: 'WINTER' });
    const { container } = render(WidgetSceneBackground);
    const bushes = container.querySelector('.bushes') as HTMLImageElement;
    expect(bushes.src).toContain(SEASON_ASSETS['WINTER']);
  });

  it('renders no weather overlay or rain when weather is CLEAR (fallback)', () => {
    const { container } = render(WidgetSceneBackground);

    expect(container.querySelector('.weather-overlay')).toBeNull();
    expect(container.querySelector('.rain-layer')).toBeNull();
  });

  it('renders cloudy ambience when weather is CLOUDY', () => {
    mockEnvStore.set({ weatherCondition: 'CLOUDY', sceneSeason: 'AUTO' });
    const { container } = render(WidgetSceneBackground);

    const overlay = container.querySelector('.weather-overlay') as HTMLImageElement;
    expect(overlay).not.toBeNull();
    expect(overlay.src).toContain(WEATHER_ASSETS['CLOUDY']);
    expect(container.querySelector('.rain-layer')).toBeNull();
  });

  it('renders weather explicitly connected by the production widget without treating it as a preview override', () => {
    mockEnvStore.set({
      weatherCondition: 'CLEAR',
      weatherStatus: 'STALE',
      sceneSeason: 'AUTO',
      effectiveTimezone: 'UTC',
      animationEnabled: true,
      widgetVisible: true,
    });
    const { container } = render(WidgetSceneBackground, {
      props: { weatherCondition: 'RAIN' },
    });

    expect((container.querySelector('.weather-overlay') as HTMLImageElement).src)
      .toContain(WEATHER_ASSETS.RAIN);
    expect(container.querySelector('.rain-layer')).not.toBeNull();
    expect(container.querySelector('.stale-indicator')).not.toBeNull();
  });

  it('renders overcast ambience when weather is OVERCAST', () => {
    mockEnvStore.set({ weatherCondition: 'OVERCAST', sceneSeason: 'AUTO' });
    const { container } = render(WidgetSceneBackground);

    const overlay = container.querySelector('.weather-overlay') as HTMLImageElement;
    expect(overlay).not.toBeNull();
    expect(overlay.src).toContain(WEATHER_ASSETS['OVERCAST']);
    expect(container.querySelector('.rain-layer')).toBeNull();
  });

  it('renders rain overlay and enables rain animation when weather is RAIN', () => {
    mockEnvStore.set({ weatherCondition: 'RAIN', sceneSeason: 'AUTO' });
    const { container } = render(WidgetSceneBackground);

    const overlay = container.querySelector('.weather-overlay') as HTMLImageElement;
    expect(overlay.src).toContain(WEATHER_ASSETS['RAIN']);

    const rainLayer = container.querySelector('.rain-layer');
    expect(rainLayer).not.toBeNull();
    const streaks = rainLayer?.querySelectorAll('.streak');
    expect(streaks?.length).toBe(RAIN_CONFIGS.RAIN.streakCount);
  });

  it('renders storm overlay and denser rain when weather is THUNDERSTORM', () => {
    mockEnvStore.set({ weatherCondition: 'THUNDERSTORM', sceneSeason: 'AUTO' });
    const { container } = render(WidgetSceneBackground);

    const overlay = container.querySelector('.weather-overlay') as HTMLImageElement;
    expect(overlay.src).toContain(WEATHER_ASSETS['THUNDERSTORM']);

    const rainLayer = container.querySelector('.rain-layer');
    expect(rainLayer).not.toBeNull();
    const streaks = rainLayer?.querySelectorAll('.streak');
    expect(streaks?.length).toBe(RAIN_CONFIGS.THUNDERSTORM.streakCount);
  });

  it('suppresses moving rain if weatherAnimationEnabled is false', () => {
    mockEnvStore.set({ weatherCondition: 'RAIN', sceneSeason: 'AUTO', animationEnabled: false, widgetVisible: true });
    const { container } = render(WidgetSceneBackground);

    expect(container.querySelector('.weather-overlay')).not.toBeNull();
    expect(container.querySelector('.rain-layer')).toBeNull();
  });
});
