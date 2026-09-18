import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { api } from '$lib/api';
import GardenSelectionContent from './GardenSelectionContent.svelte';

vi.mock('$lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn() },
  APIError: class extends Error {},
}));

describe('GardenSelectionContent', () => {
  it('navigates every catalog plant using the arrows', async () => {
    const names = ['Monstera', 'Sunflower', 'Bonsai', 'Jasmine', 'Lavender'];
    vi.mocked(api.get).mockResolvedValue({
      water_balance: 9,
      leaves_balance: 12,
      vitality: 100,
      selected_plant_id: null,
      growth_stage: 'SPROUTING',
      catalog: names.map((name, index) => ({
        id: String(index),
        species: name.toLowerCase(),
        name,
        description: `${name} description`,
        unlock_cost: index * 10,
        is_unlocked: false,
        is_selected: false,
      })),
    });

    render(GardenSelectionContent);
    expect(await screen.findByRole('heading', { name: 'Monstera' })).toBeInTheDocument();
    expect(screen.queryByLabelText(/Water balance/)).not.toBeInTheDocument();
    expect(screen.getByLabelText('Unlock cost: 0 leaves')).toBeInTheDocument();
    expect(screen.queryByLabelText('All plants')).not.toBeInTheDocument();

    const user = userEvent.setup();
    for (const name of names.slice(1)) {
      await user.click(screen.getByRole('button', { name: 'Next plant' }));
      expect(screen.getByRole('heading', { name })).toBeInTheDocument();
    }
    await user.click(screen.getByRole('button', { name: 'Previous plant' }));
    expect(screen.getByRole('heading', { name: 'Jasmine' })).toBeInTheDocument();
  });

  it('unlocks and selects the free plant through the garden API', async () => {
    const garden = {
      water_balance: 0,
      leaves_balance: 0,
      vitality: 100,
      selected_plant_id: null as string | null,
      growth_stage: 'SPROUTING',
      catalog: [{
        id: 'monstera-id', species: 'monstera', name: 'Monstera',
        description: 'A houseplant', unlock_cost: 0,
        is_unlocked: false, is_selected: false,
      }],
    };
    vi.mocked(api.get).mockResolvedValue(garden);
    vi.mocked(api.post).mockImplementation(async (path) => {
      if (path.endsWith('/unlock')) garden.catalog[0].is_unlocked = true;
      if (path.endsWith('/select')) {
        garden.selected_plant_id = 'monstera-id';
        garden.catalog[0].is_selected = true;
      }
      return { ...garden, catalog: garden.catalog.map((plant) => ({ ...plant })) };
    });

    render(GardenSelectionContent);
    const user = userEvent.setup();
    await user.click(await screen.findByRole('button', { name: 'UNLOCK' }));
    expect(api.post).toHaveBeenCalledWith('/garden/plants/monstera-id/unlock');
    await user.click(await screen.findByRole('button', { name: 'SELECT' }));
    expect(api.post).toHaveBeenCalledWith('/garden/plants/monstera-id/select');
    expect(await screen.findByRole('button', { name: 'SELECTED' })).toBeDisabled();
  });
});
