import { render } from '@testing-library/svelte';
import { tick } from 'svelte';
import { afterEach, expect, it, vi } from 'vitest';
import RainLayer from './RainLayer.svelte';
import { RAIN_CONFIGS } from '../../model/environment';

afterEach(() => { vi.unstubAllGlobals(); });

it('renders denser storm rain and respects the animation setting and widget state', async () => {
  const view = render(RainLayer, { props: { weather: 'RAIN', enabled: true } });
  expect(view.container.querySelectorAll('.streak')).toHaveLength(RAIN_CONFIGS.RAIN.streakCount);
  await view.rerender({ weather: 'THUNDERSTORM', enabled: true });
  expect(view.container.querySelectorAll('.streak')).toHaveLength(RAIN_CONFIGS.THUNDERSTORM.streakCount);
  await view.rerender({ weather: 'RAIN', enabled: false });
  expect(view.container.querySelector('.rain-layer')).toBeNull();
  await view.rerender({ weather: 'RAIN', enabled: true, widgetHidden: true });
  expect(view.container.querySelector('.rain-layer')).toBeNull();
});

it('responds to reduced motion and document visibility and removes listeners', async () => {
  let motion = false;
  const callbacks = new Set<() => void>();
  const media = {
    get matches() { return motion; },
    addEventListener: vi.fn((_event, callback) => callbacks.add(callback)),
    removeEventListener: vi.fn((_event, callback) => callbacks.delete(callback)),
  };
  vi.stubGlobal('matchMedia', vi.fn(() => media));
  const view = render(RainLayer, { props: { weather: 'RAIN' } });
  expect(view.container.querySelector('.rain-layer')).not.toBeNull();
  motion = true;
  callbacks.forEach((callback) => callback());
  await tick();
  expect(view.container.querySelector('.rain-layer')).toBeNull();
  motion = false;
  callbacks.forEach((callback) => callback());
  await tick();
  expect(view.container.querySelector('.rain-layer')).not.toBeNull();
  Object.defineProperty(document, 'hidden', { configurable: true, value: true });
  document.dispatchEvent(new Event('visibilitychange'));
  await tick();
  expect(view.container.querySelector('.rain-layer')).toBeNull();
  view.unmount();
  expect(callbacks.size).toBe(0);
  Object.defineProperty(document, 'hidden', { configurable: true, value: false });
});
