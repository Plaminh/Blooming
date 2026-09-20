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

test('failed message is marked as failed and excluded from outgoing history on retry', async () => {
  // 1. Initial success
  vi.mocked(api.post).mockResolvedValueOnce({
    reply: 'First reply', draft: null
  });
  await mrBloomStore.submitMessage('First message');

  // 2. Failure
  vi.mocked(api.post).mockRejectedValueOnce(new Error('Network error'));
  await mrBloomStore.submitMessage('Failing message');

  let state = get(mrBloomStore);
  expect(state.error).toBe('Network error');
  const failedMsg = state.chatHistory.at(-1)!;
  expect(failedMsg.content).toBe('Failing message');
  expect(failedMsg.status).toBe('failed');

  // 3. Retry success
  vi.mocked(api.post).mockResolvedValueOnce({
    reply: 'Recovered reply', draft: null
  });
  await mrBloomStore.retryMessage(failedMsg.id);

  state = get(mrBloomStore);
  expect(state.error).toBeNull();
  
  expect(api.post).toHaveBeenLastCalledWith(
    '/assistant/chat',
    expect.objectContaining({
      message: 'Failing message',
      history: [
        { role: 'user', content: 'First message' },
        { role: 'assistant', content: 'First reply' }
      ]
    })
  );

  const userMessages = state.chatHistory.filter(m => m.role === 'user');
  expect(userMessages.length).toBe(2);
  expect(userMessages[1].status).toBeUndefined(); // Status cleared
});
