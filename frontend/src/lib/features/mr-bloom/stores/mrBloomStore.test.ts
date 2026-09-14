import { expect, test, vi, beforeEach, afterEach } from 'vitest';
import { get } from 'svelte/store';
import { mrBloomStore } from './mrBloomStore';

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

test('mrBloomStore mock generation flow', async () => {
  // Initial state
  let state = get(mrBloomStore);
  expect(state.previewMode).toBe('placeholder');
  expect(state.activeDraft).toBeNull();
  expect(state.chatHistory.length).toBe(1);
  
  // Submit today plan request
  mrBloomStore.submitMessage('Plan my day. I have 6 hours.');
  
  state = get(mrBloomStore);
  expect(state.isWaitingForResponse).toBe(true);
  expect(state.chatHistory.length).toBe(2);
  
  // Fast forward mock AI delay
  vi.advanceTimersByTime(800);
  
  state = get(mrBloomStore);
  expect(state.isWaitingForResponse).toBe(false);
  expect(state.previewMode).toBe('today');
  expect(state.activeDraft?.type).toBe('today');
  expect(state.chatHistory.length).toBe(3);
  
  // Test generating timeline
  mrBloomStore.generateTimeline();
  state = get(mrBloomStore);
  expect(state.previewMode).toBe('timeline');
  
  // Back to tasks
  mrBloomStore.backToTasks();
  state = get(mrBloomStore);
  expect(state.previewMode).toBe('today');
  
  // Discard draft
  mrBloomStore.discardDraft();
  state = get(mrBloomStore);
  expect(state.previewMode).toBe('placeholder');
  expect(state.activeDraft).toBeNull();
});
