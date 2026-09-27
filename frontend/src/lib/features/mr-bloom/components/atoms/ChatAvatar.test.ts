import { fireEvent, render } from '@testing-library/svelte';
import { tick } from 'svelte';
import { get } from 'svelte/store';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import ChatAvatar from './ChatAvatar.svelte';
import MrBloomConversationPanel from '../organisms/MrBloomConversationPanel.svelte';
import { mrBloomStore } from '../../stores/mrBloomStore';
import { api } from '$lib/api';

const initialState = get(mrBloomStore);

beforeEach(() => {
  vi.useFakeTimers();
  vi.stubGlobal('matchMedia', vi.fn(() => ({
    matches: false, addEventListener: vi.fn(), removeEventListener: vi.fn()
  })));
});

afterEach(() => {
  mrBloomStore.set(initialState);
  vi.useRealTimers();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

test('blinks while idle, switches to thinking frames, and resets after replying', async () => {
  const { container, rerender, unmount } = render(ChatAvatar);
  const character = () => container.querySelector('.character');
  await tick();
  expect(character()).toHaveAttribute('data-animation', 'idle');
  expect(character()).toHaveAttribute('data-row', '0');
  expect(character()).toHaveAttribute('data-frame', '2');
  expect(container.querySelector('.avatar-leaf')).toBeNull();
  expect(container.querySelector('.sheet')).toHaveAttribute('src', '/assets/mr-bloom/mr-bloom-spritesheet.png');
  await vi.advanceTimersByTimeAsync(3000);
  expect(character()).toHaveAttribute('data-frame', '1');
  await vi.advanceTimersByTimeAsync(140);
  expect(character()).toHaveAttribute('data-frame', '2');

  await rerender({ thinking: true });
  expect(character()).toHaveAttribute('data-row', '2');
  expect(character()).toHaveAttribute('data-frame', '0');
  for (const frame of [1, 2, 3, 0]) {
    await vi.advanceTimersByTimeAsync(250);
    expect(character()).toHaveAttribute('data-frame', String(frame));
  }
  await rerender({ thinking: false });
  expect(character()).toHaveAttribute('data-animation', 'idle');
  expect(character()).toHaveAttribute('data-frame', '2');
  const clearTimer = vi.spyOn(window, 'clearTimeout');
  unmount();
  expect(clearTimer).toHaveBeenCalled();
});

test('keeps the avatar still when reduced motion is requested', async () => {
  vi.stubGlobal('matchMedia', vi.fn(() => ({
    matches: true, addEventListener: vi.fn(), removeEventListener: vi.fn()
  })));
  const { container, rerender } = render(ChatAvatar);
  await tick();
  await vi.advanceTimersByTimeAsync(6000);
  expect(container.querySelector('.character')).toHaveAttribute('data-frame', '2');
  await rerender({ thinking: true });
  await vi.advanceTimersByTimeAsync(1000);
  expect(container.querySelector('.character')).toHaveAttribute('data-frame', '0');
});

test('shows thinking animation only for a pending response', async () => {
  let resolveReply!: (value: { reply: string; draft: null }) => void;
  vi.spyOn(api, 'post').mockReturnValue(new Promise(resolve => { resolveReply = resolve; }));
  const { container, getByRole, unmount } = render(MrBloomConversationPanel);
  expect(container.querySelector('[data-animation="thinking"]')).toBeNull();
  await fireEvent.click(getByRole('button', { name: /PLAN MY DAY/ }));
  expect(container.querySelector('.loading-container [data-animation="thinking"]')).toBeInTheDocument();
  expect(container.querySelector('.chat-message [data-animation="idle"]')).toBeInTheDocument();
  resolveReply({ reply: 'Here is your plan.', draft: null });
  await vi.advanceTimersByTimeAsync(800);
  expect(container.querySelector('.loading-container')).toBeNull();
  expect(container.querySelector('[data-animation="thinking"]')).toBeNull();
  expect(container.querySelectorAll('.chat-message [data-animation="idle"]')).toHaveLength(2);
  unmount();
});
