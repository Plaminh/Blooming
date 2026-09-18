import { describe, it, expect, vi } from 'vitest';
import { render, waitFor } from '@testing-library/svelte';
import GardenPanel from './GardenPanel.svelte';
import { api } from '$lib/api';
import { notifyGardenUpdated } from '$lib/features/garden-selection/model/gardenUpdates';
import { WIDGET_SCENE } from '$lib/features/companion-widget/model/atlas';

vi.mock('$lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn() },
  APIError: class extends Error {},
}));

describe('GardenPanel', () => {
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
    expect(container.querySelector('.garden-scene .sky')).toHaveAttribute('src', WIDGET_SCENE.skySrc);
    expect(container.querySelector('.garden-scene .bushes')).toHaveAttribute('src', WIDGET_SCENE.bushesSrc);
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
