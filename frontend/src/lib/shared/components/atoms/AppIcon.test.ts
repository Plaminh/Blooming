import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import AppIcon, { ICON_NAMES, type IconName } from './AppIcon.svelte';

const imageAssets = {
  sprout: '/assets/icons/leaf-icon.png',
  water: '/assets/icons/water-icon.png'
};

describe('AppIcon', () => {
  it.each(ICON_NAMES)('renders intended geometry for %s without either fallback', (name) => {
    const { container } = render(AppIcon, { name });
    expect(container.querySelector('svg, img')).not.toBeNull();
    expect(container.querySelector('[data-error="true"]')).toBeNull();
    expect(container.querySelector('rect[x="2"][y="2"][width="20"][height="20"][rx="4"]')).toBeNull();

    if (name === 'sprout' || name === 'water') {
      // Raster icons use their intended image asset instead of SVG geometry.
      expect(container.querySelector('img')).toHaveAttribute('src', imageAssets[name]);
    } else {
      const svg = container.querySelector('svg');
      expect(svg).not.toBeNull();
      expect(svg?.querySelector('path, circle, rect, ellipse, polyline, polygon, line')).not.toBeNull();
    }
  });

  it('renders currentColor error geometry for an unknown name', () => {
    const { container } = render(AppIcon, { name: 'unknown_invalid_icon_name' as IconName });
    expect(container.querySelector('svg [data-error="true"]')).toHaveAttribute('stroke', 'currentColor');
  });
});
