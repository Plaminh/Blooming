import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import StatusBadge from './StatusBadge.svelte';

describe('StatusBadge', () => {
  describe('tag variant', () => {
    it('renders Core tag badge', () => {
      const { container } = render(StatusBadge, { status: 'Core' });
      const badge = container.querySelector('.status-badge.tag');
      expect(badge).not.toBeNull();
      expect(badge?.textContent?.trim()).toBe('Core');
    });

    it('renders Optional tag badge', () => {
      const { container } = render(StatusBadge, { status: 'Optional' });
      const badge = container.querySelector('.status-badge.tag');
      expect(badge).not.toBeNull();
      expect(badge?.textContent?.trim()).toBe('Optional');
    });
  });

  describe('pill variant', () => {
    it('renders Completed pill badge', () => {
      const { container } = render(StatusBadge, { variant: 'pill', status: 'Completed' });
      const badge = container.querySelector('.status-badge.pill');
      expect(badge).not.toBeNull();
      expect(badge?.classList.contains('completed')).toBe(true);
    });

    it('renders Unfinished pill badge', () => {
      const { container } = render(StatusBadge, { variant: 'pill', status: 'Unfinished' });
      const badge = container.querySelector('.status-badge.pill');
      expect(badge).not.toBeNull();
      expect(badge?.classList.contains('unfinished')).toBe(true);
    });
  });
});
