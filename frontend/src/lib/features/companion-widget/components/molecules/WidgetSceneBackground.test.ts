import { render } from '@testing-library/svelte';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import WidgetSceneBackground from './WidgetSceneBackground.svelte';
import { DAYTIME_ASSETS, SEASON_ASSETS, WEATHER_ASSETS, RAIN_CONFIGS } from '../../model/environment';

describe('WidgetSceneBackground', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders correct daytime and season assets based on local time', () => {
    // Set time to 9:00 AM in May
    const fakeDate = new Date('2023-05-15T02:00:00Z'); // 9 AM in Ho Chi Minh City
    vi.setSystemTime(fakeDate);

    const { container } = render(WidgetSceneBackground, { props: { timezone: 'Asia/Ho_Chi_Minh' } });

    const sky = container.querySelector('.sky') as HTMLImageElement;
    expect(sky.src).toContain(DAYTIME_ASSETS['MORNING']);

    const bushes = container.querySelector('.bushes') as HTMLImageElement;
    expect(bushes.src).toContain(SEASON_ASSETS['SPRING']);
  });

  it('renders no weather overlay or rain when weather is CLEAR (fallback)', () => {
    const { container } = render(WidgetSceneBackground, { props: { weather: 'CLEAR' } });

    expect(container.querySelector('.weather-overlay')).toBeNull();
    expect(container.querySelector('.rain-layer')).toBeNull();
  });

  it('renders cloudy ambience when weather is CLOUDY', () => {
    const { container } = render(WidgetSceneBackground, { props: { weather: 'CLOUDY' } });

    const overlay = container.querySelector('.weather-overlay') as HTMLImageElement;
    expect(overlay).not.toBeNull();
    expect(overlay.src).toContain(WEATHER_ASSETS['CLOUDY']);
    expect(container.querySelector('.rain-layer')).toBeNull();
  });

  it('renders overcast ambience when weather is OVERCAST', () => {
    const { container } = render(WidgetSceneBackground, { props: { weather: 'OVERCAST' } });

    const overlay = container.querySelector('.weather-overlay') as HTMLImageElement;
    expect(overlay).not.toBeNull();
    expect(overlay.src).toContain(WEATHER_ASSETS['OVERCAST']);
    expect(container.querySelector('.rain-layer')).toBeNull();
  });

  it('renders rain overlay and enables rain animation when weather is RAIN', () => {
    const { container } = render(WidgetSceneBackground, { props: { weather: 'RAIN' } });

    const overlay = container.querySelector('.weather-overlay') as HTMLImageElement;
    expect(overlay.src).toContain(WEATHER_ASSETS['RAIN']);

    const rainLayer = container.querySelector('.rain-layer');
    expect(rainLayer).not.toBeNull();
    const streaks = rainLayer?.querySelectorAll('.streak');
    expect(streaks?.length).toBe(RAIN_CONFIGS.RAIN.streakCount);
  });

  it('renders storm overlay and denser rain when weather is THUNDERSTORM', () => {
    const { container } = render(WidgetSceneBackground, { props: { weather: 'THUNDERSTORM' } });

    const overlay = container.querySelector('.weather-overlay') as HTMLImageElement;
    expect(overlay.src).toContain(WEATHER_ASSETS['THUNDERSTORM']);

    const rainLayer = container.querySelector('.rain-layer');
    expect(rainLayer).not.toBeNull();
    const streaks = rainLayer?.querySelectorAll('.streak');
    expect(streaks?.length).toBe(RAIN_CONFIGS.THUNDERSTORM.streakCount);
  });

  it('has denser rain in THUNDERSTORM than RAIN', () => {
    expect(RAIN_CONFIGS.THUNDERSTORM.streakCount).toBeGreaterThan(RAIN_CONFIGS.RAIN.streakCount);
  });

  it('suppresses moving rain if rainEnabled is false', () => {
    const { container } = render(WidgetSceneBackground, { props: { weather: 'RAIN', rainEnabled: false } });

    expect(container.querySelector('.weather-overlay')).not.toBeNull();
    // rain-layer should not be in the document
    expect(container.querySelector('.rain-layer')).toBeNull();
  });
});
