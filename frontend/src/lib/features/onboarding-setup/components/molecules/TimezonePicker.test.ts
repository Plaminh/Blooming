import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import TimezonePicker from './TimezonePicker.svelte';

describe('TimezonePicker', () => {
  it('searches the full list and commits a manual selection', async () => {
    const user = userEvent.setup();
    render(TimezonePicker, { props: { id: 'timezone', value: 'UTC' } });
    const input = screen.getByRole('combobox');
    await user.click(input);
    expect(screen.getAllByRole('option').length).toBeGreaterThan(100);
    const list = screen.getByRole('listbox');
    expect(list).toHaveClass('timezone-options');
    expect(list).toHaveAttribute('data-scrollable', 'true');
    await user.clear(input);
    await user.type(input, 'Ho Chi Minh');
    await user.click(screen.getByRole('button', { name: 'Asia/Ho_Chi_Minh' }));
    expect(input).toHaveValue('Asia/Ho_Chi_Minh');
    await user.clear(input);
    await user.type(input, 'Tokyo');
    expect(screen.getByRole('button', { name: 'Asia/Tokyo' })).toBeInTheDocument();
  });

  it('Enter selects a timezone without submitting a parent form', async () => {
    const user = userEvent.setup();
    const submit = vi.fn((event: SubmitEvent) => event.preventDefault());
    const { container } = render(TimezonePicker, { props: { id: 'timezone', value: 'UTC' } });
    container.addEventListener('submit', submit as unknown as EventListener);
    const input = screen.getByRole('combobox');
    await user.clear(input);
    await user.type(input, 'Asia/Tokyo{Enter}');
    expect(input).toHaveValue('Asia/Tokyo');
    expect(submit).not.toHaveBeenCalled();
  });
});
