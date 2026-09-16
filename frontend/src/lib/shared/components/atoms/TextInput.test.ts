import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import TextInput from './TextInput.svelte';

describe('TextInput', () => {
  it('renders a standard input by default without a label', () => {
    const { getByRole, container } = render(TextInput);
    expect(getByRole('textbox')).toHaveClass('standard');
    expect(container.querySelector('label')).toBeNull();
  });

  it.each(['standard', 'composer'] as const)('supports value, input, placeholder and keyboard events in the %s variant', async (variant) => {
    const onkeydown = vi.fn();
    const { getByRole, getByPlaceholderText } = render(TextInput, {
      variant, value: 'Initial text', placeholder: 'Write a message', onkeydown
    });
    const input = getByRole('textbox');
    expect(input).toHaveClass(variant);
    expect(input).toHaveValue('Initial text');
    expect(getByPlaceholderText('Write a message')).toBe(input);

    await fireEvent.input(input, { target: { value: 'Updated text' } });
    expect(input).toHaveValue('Updated text');
    await fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    expect(onkeydown).toHaveBeenCalledOnce();
    expect(onkeydown).toHaveBeenCalledWith(expect.objectContaining({ key: 'Enter', target: input }));
  });

  it('connects the visible label to the input ID', () => {
    const { getByLabelText } = render(TextInput, { id: 'test-field', label: 'My Label' });
    expect(getByLabelText('My Label')).toHaveAttribute('id', 'test-field');
  });

  it('connects validation text to the invalid input through its real ID', () => {
    const { getByRole, getByText } = render(TextInput, { id: 'field', label: 'Field', error: 'Required' });
    const input = getByRole('textbox', { name: 'Field' });
    const error = getByText('Required');
    expect(error.id).toBe('field-error');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAttribute('aria-describedby', error.id);
    expect(document.getElementById(input.getAttribute('aria-describedby')!)).toBe(error);
    expect(input).toHaveAccessibleDescription('Required');
  });

  it('does not mark an input invalid or describe an error when valid', () => {
    const { getByRole } = render(TextInput, { id: 'field', label: 'Field' });
    expect(getByRole('textbox')).toHaveAttribute('aria-invalid', 'false');
    expect(getByRole('textbox')).not.toHaveAttribute('aria-describedby');
  });

  it.each(['standard', 'composer'] as const)('disables the %s input', (variant) => {
    const { getByRole } = render(TextInput, { variant, disabled: true });
    expect(getByRole('textbox')).toBeDisabled();
  });
});
