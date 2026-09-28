import { describe, it, expect, vi } from 'vitest';
import { render, waitFor } from '@testing-library/svelte';
import GardenPanel from './GardenPanel.svelte';
import { api } from '$lib/api';
import { notifyGardenUpdated } from '$lib/features/garden-selection/model/gardenUpdates';
import { DAYTIME_ASSETS, SEASON_ASSETS, getDaytimeFromHour, getSeasonFromMonth } from '$lib/features/companion-widget/model/environment';
import { environmentStore } from '$lib/shared/stores/environmentStore';


vi.mock('$lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn() },
  APIError: class extends Error {},
}));

describe('GardenPanel', () => {
  it('updates its scene when the shared environment changes', async () => {
    environmentStore.resetForTests();
    vi.mocked(api.get).mockImplementation(async (path: string) => {
      if (path === '/me/settings') return {
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        weather_enabled: true, weather_lat: 10, scene_season: 'AUTO',
        weather_animation_enabled: false, widget_visibility: true,
      };
      if (path === '/weather/current') return {
        condition: 'THUNDERSTORM', status: 'OK', updated_at: '2026-09-19T00:00:00Z',
      };
      return { water_balance: 0, leaves_balance: 0, vitality: 100, catalog: [] };
    });
    const { container } = render(GardenPanel);
    await environmentStore.refresh();
    await waitFor(() => expect(container.querySelector('.garden-scene')?.getAttribute('data-weather')).toBe('THUNDERSTORM'));
    expect((container.querySelector('.weather-overlay') as HTMLImageElement).src).toContain('storm-overlay');
    environmentStore.resetForTests();
  });
  it('links to plant selection and shows the unlocked count', () => {
    const { container } = render(GardenPanel);
    const link = container.querySelector('a.garden');
    expect(link?.getAttribute('href')).toBe('/garden-selection');
    expect(link?.querySelector('h2')?.textContent).toBe('YOUR GARDEN');
    const footer = container.querySelector('.garden-footer');
    expect(footer?.textContent).toContain('UNLOCKED PLANTS');
  });

  it('uses the widget sky and bushes without characters or plants', () => {
    const { container } = render(GardenPanel);
    const now = new Date();
    const hour = now.getHours();
    const month = now.getMonth();
    const daytime = getDaytimeFromHour(hour);
    const season = getSeasonFromMonth(month);
    expect((container.querySelector('.garden-scene .sky') as HTMLImageElement).src).toContain(DAYTIME_ASSETS[daytime]);
    expect((container.querySelector('.garden-scene .bushes') as HTMLImageElement).src).toContain(SEASON_ASSETS[season]);
    expect(container.querySelector('.garden-scene [data-species]')).not.toBeInTheDocument();
    expect(container.querySelector('.garden-scene .flower')).not.toBeInTheDocument();
  });

  it('refreshes the unlocked count after a garden update', async () => {
    const catalog = [
      { id: 'a', species: 'monstera', name: 'Monstera', description: 'Plant', unlock_cost: 0, is_unlocked: true, is_selected: true },
      { id: 'b', species: 'sunflower', name: 'Sunflower', description: 'Plant', unlock_cost: 10, is_unlocked: false, is_selected: false },
    ];
    const garden = {
      water_balance: 0, leaves_balance: 10, vitality: 100,
      growth_stage: 'SPROUTING', selected_plant_id: 'a', catalog,
    };
    vi.mocked(api.get).mockResolvedValue(garden);

    const { container } = render(GardenPanel);
    await waitFor(() => expect(container.querySelector('.garden-footer span')?.textContent).toBe('1 / 2'));

    vi.mocked(api.get).mockResolvedValue({
      ...garden, selected_plant_id: 'b',
      catalog: catalog.map((plant) => ({ ...plant, is_unlocked: true, is_selected: plant.id === 'b' })),
    });
    notifyGardenUpdated();

    await waitFor(() => expect(container.querySelector('.garden-footer span')?.textContent).toBe('2 / 2'));
  });
});
