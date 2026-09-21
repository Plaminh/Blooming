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

test('ChatComposer does not submit on Shift+Enter and inserts newline', async () => {
  const submitHandler = vi.fn();
  const { getByRole } = render(ChatComposer, {
    props: { value: 'Valid text', disabled: false, onsubmit: submitHandler }
  });
  const input = getByRole('textbox') as HTMLTextAreaElement;
  
  const userEvent = (await import('@testing-library/user-event')).default;
  await userEvent.type(input, '{Shift>}{Enter}{/Shift}Line 2');
  
  expect(submitHandler).not.toHaveBeenCalled();
  expect(input.value).toBe('Valid text\nLine 2');
});

test('ChatComposer does not submit when composing (IME) but submits after compositionend', async () => {
  const submitHandler = vi.fn();
  const { getByRole, rerender } = render(ChatComposer, {
    props: { value: 'Valid text', disabled: false, onsubmit: submitHandler }
  });
  const input = getByRole('textbox');
  
  // Enter while composing
  const composingEvent = new KeyboardEvent('keydown', { key: 'Enter' });
  Object.defineProperty(composingEvent, 'isComposing', { value: true });
  await fireEvent(input, composingEvent);
  expect(submitHandler).not.toHaveBeenCalled();
  
  // Enter after compositionend
  await fireEvent.keyDown(input, { key: 'Enter', isComposing: false, keyCode: 13 });
  expect(submitHandler).toHaveBeenCalledWith('Valid text');
});
