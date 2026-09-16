import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import GardenPanel from './GardenPanel.svelte';

describe('GardenPanel (smoke)', () => {
  it('renders the garden link panel', () => {
    const { container } = render(GardenPanel);
    const panel = container.querySelector('.garden');
    expect(panel).not.toBeNull();
  });

  it('shows the YOUR GARDEN heading', () => {
    const { container } = render(GardenPanel);
    const heading = container.querySelector('h2');
    expect(heading?.textContent).toBe('YOUR GARDEN');
  });

  it('panel is a link pointing to /garden-selection', () => {
    const { container } = render(GardenPanel);
    const link = container.querySelector('a.garden');
    expect(link?.getAttribute('href')).toBe('/garden-selection');
  });

  it('shows the UNLOCKED PLANTS counter footer', () => {
    const { container } = render(GardenPanel);
    const footer = container.querySelector('.garden-footer');
    expect(footer).not.toBeNull();
    expect(footer?.textContent).toContain('UNLOCKED PLANTS');
  });
});
