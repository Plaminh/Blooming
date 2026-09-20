import { render } from '@testing-library/svelte';
import { afterEach, expect, it, vi } from 'vitest';
import PreviewPage from './+page.svelte';
import { page } from '$app/state';
import { DAYTIME_ASSETS, SEASON_ASSETS, WEATHER_ASSETS } from '$lib/features/companion-widget/model/environment';

vi.mock('$app/state', () => ({ page: { url: new URL('http://localhost/widget-preview') } }));
afterEach(() => { page.url.search = ''; });

it.each([
  ['NIGHT', 'OVERCAST', 'WINTER'],
  ['NIGHT', 'THUNDERSTORM', 'WINTER'],
  ['SUNSET', 'CLOUDY', 'SUMMER'],
  ['NIGHT', 'RAIN', 'WINTER'],
] as const)('propagates %s, %s, %s through the preview route', (time, weather, season) => {
  page.url.search = `?time=${time}&weather=${weather}&season=${season}`;
  const view = render(PreviewPage);
  expect((view.container.querySelector('.sky') as HTMLImageElement).src).toContain(DAYTIME_ASSETS[time]);
  expect((view.container.querySelector('.bushes') as HTMLImageElement).src).toContain(SEASON_ASSETS[season]);
  expect((view.container.querySelector('.weather-overlay') as HTMLImageElement).src).toContain(WEATHER_ASSETS[weather]!);
});

it('falls back for invalid parameters and supports partial overrides', () => {
  page.url.search = '?time=BAD&season=BAD&weather=RAIN';
  const view = render(PreviewPage);
  expect(view.container.querySelector('.sky')).not.toBeNull();
  expect(view.container.querySelector('.bushes')).not.toBeNull();
  expect((view.container.querySelector('.weather-overlay') as HTMLImageElement).src).toContain(WEATHER_ASSETS.RAIN!);
});

it('renders without query parameters', () => {
  const view = render(PreviewPage);
  expect(view.container.querySelector('.sky')).not.toBeNull();
  expect(view.container.querySelector('.bushes')).not.toBeNull();
});
