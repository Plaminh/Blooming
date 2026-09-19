import { beforeEach, expect, test, vi } from 'vitest';
import { get } from 'svelte/store';
import { api } from '$lib/api';
import { mrBloomStore } from './mrBloomStore';

vi.mock('$lib/api', () => ({ api: { post: vi.fn() } }));

beforeEach(() => {
  vi.clearAllMocks();
  mrBloomStore.set({ chatHistory: [], isWaitingForResponse: false, activeDraft: null, previewMode: 'placeholder', error: null });
});

test('sends the message to the backend and shows its draft', async () => {
  vi.mocked(api.post).mockResolvedValue({
    reply: 'Review these tasks.',
    draft: { type: 'today', availability: { start: '09:00', end: '12:00', totalHours: 3 }, tasks: [
      { title: 'Write report', durationMin: 90, priority: 'Core' }
    ] }
  });

  await mrBloomStore.submitMessage('Plan my report');

  expect(api.post).toHaveBeenCalledWith('/assistant/chat', { message: 'Plan my report', history: [] });
  const state = get(mrBloomStore);
  expect(state.chatHistory.at(-1)?.content).toBe('Review these tasks.');
  expect(state.activeDraft?.type).toBe('today');
  if (state.activeDraft?.type === 'today') expect(state.activeDraft.tasks[0].title).toBe('Write report');
  expect(state.isWaitingForResponse).toBe(false);
});

test('shows a service error and keeps the composer available', async () => {
  vi.mocked(api.post).mockRejectedValue(new Error('Service unavailable'));
  await mrBloomStore.submitMessage('Help me plan');
  const state = get(mrBloomStore);
  expect(state.error).toBe('Service unavailable');
  expect(state.isWaitingForResponse).toBe(false);
  expect(state.activeDraft).toBeNull();
});
