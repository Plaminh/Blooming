import { render, fireEvent } from '@testing-library/svelte';
import { expect, test, vi } from 'vitest';
import ChatComposer from './ChatComposer.svelte';

test('ChatComposer does not submit when empty or disabled', async () => {
  const submitHandler = vi.fn();
  
  const { getByRole, rerender } = render(ChatComposer, {
    props: {
      value: '',
      disabled: false,
      onsubmit: submitHandler
    }
  });

  const button = getByRole('button', { name: 'Send' });
  const input = getByRole('textbox');
  
  // Empty submit
  expect(button).toBeDisabled();
  await fireEvent.keyDown(input, { key: 'Enter' });
  expect(submitHandler).not.toHaveBeenCalled();
  
  // Whitespace submit
  await rerender({ value: '   ', disabled: false, onsubmit: submitHandler });
  expect(button).toBeDisabled();
  await fireEvent.keyDown(input, { key: 'Enter' });
  expect(submitHandler).not.toHaveBeenCalled();
  
  // Disabled submit with valid text
  await rerender({ value: 'Valid text', disabled: true, onsubmit: submitHandler });
  expect(button).toBeDisabled();
  await fireEvent.keyDown(input, { key: 'Enter' });
  expect(submitHandler).not.toHaveBeenCalled();
  
  // Valid submit
  await rerender({ value: 'Valid text', disabled: false, onsubmit: submitHandler });
  expect(button).not.toBeDisabled();
  await fireEvent.click(button);
  expect(submitHandler).toHaveBeenCalledWith('Valid text');
});
