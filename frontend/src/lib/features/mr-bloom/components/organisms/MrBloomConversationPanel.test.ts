import { render, fireEvent, waitFor } from '@testing-library/svelte';
import { expect, test, vi, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { tick } from 'svelte';
import MrBloomConversationPanel from './MrBloomConversationPanel.svelte';
import { mrBloomStore } from '../../stores/mrBloomStore';
import { api } from '$lib/api';

vi.mock('$lib/api', () => ({
  api: { post: vi.fn(), get: vi.fn() }
}));

beforeEach(() => {
  vi.clearAllMocks();
  mrBloomStore.set({ 
    chatHistory: [], 
    isWaitingForResponse: false, 
    activeDraft: null, 
    preview: null, 
    previewMode: 'placeholder', 
    sessionId: null, 
    degraded: null, 
    suggestions: [], 
    assumptions: [], 
    needsReplace: false, 
    error: null 
  });
});

test('UI-001: Renders conversation UI', () => {
  const { getByRole, getByPlaceholderText } = render(MrBloomConversationPanel);
  // Chat input
  expect(getByPlaceholderText(/Choose what you want to plan first/i)).toBeInTheDocument();
  // Send control
  expect(getByRole('button', { name: 'Send' })).toBeInTheDocument();
});

test('UI-002, UI-003, UI-004, UI-007, UI-011: Message lifecycle and sending', async () => {
  let resolveApi: (val: any) => void;
  const apiPromise = new Promise(resolve => {
    resolveApi = resolve;
  });
  
  vi.mocked(api.post).mockReturnValue(apiPromise);
  
  const { container, getByRole, getByPlaceholderText, getAllByText, queryByRole } = render(MrBloomConversationPanel);
  
  const input = getByPlaceholderText(/Choose what you want to plan first/i);
  
  // Enter text
  await fireEvent.input(input, { target: { value: 'Hello Mr. Bloom' } });
  
  // UI-004: Enter sends
  await fireEvent.keyDown(input, { key: 'Enter' });
  
  // API called exactly once
  expect(api.post).toHaveBeenCalledTimes(1);
  expect(api.post).toHaveBeenCalledWith('/assistant/chat', expect.objectContaining({ message: 'Hello Mr. Bloom' }));
  
  // UI-003: User message appears exactly once (optimistic)
  expect(getAllByText('Hello Mr. Bloom')).toHaveLength(1);
  
  // Input should be cleared
  expect((input as HTMLTextAreaElement).value).toBe('');
  
  // UI-007: Waiting state is visible
  expect(get(mrBloomStore).isWaitingForResponse).toBe(true);
  const waitingIndicator = queryByRole('status', { name: /waiting for response/i });
  expect(waitingIndicator).toBeInTheDocument();
  
  // Now resolve the API
  resolveApi!({ reply: 'Hello User, how can I help?', draft: null });
  
  await waitFor(() => {
    // Waiting state disappears
    expect(get(mrBloomStore).isWaitingForResponse).toBe(false);
    expect(queryByRole('status', { name: /waiting for response/i })).not.toBeInTheDocument();
  });
  
  // Assistant reply appears
  expect(getAllByText('Hello User, how can I help?')).toHaveLength(1);
  
  // UI-011: Message ordering
  // Check DOM order explicitly instead of store
  const bubbles = Array.from(container.querySelectorAll('.bubble'));
  expect(bubbles).toHaveLength(2);
  expect(bubbles[0].textContent?.trim()).toContain('Hello Mr. Bloom');
  expect(bubbles[1].textContent?.trim()).toContain('Hello User, how can I help?');
  
  // User message still exactly once
  expect(getAllByText('Hello Mr. Bloom')).toHaveLength(1);
});

test('UI-013: Auto-scroll', async () => {
  const { container } = render(MrBloomConversationPanel);
  
  // Find the scrolling container
  // It uses bind:this={messagesContainer}, and reads scrollHeight.
  // We can spy on the DOM property or simply verify that the effect runs tick() and sets scrollTop.
  const messagesContainer = container.querySelector('.messages-container') as HTMLDivElement;
  expect(messagesContainer).not.toBeNull();
  
  // Mock scrollHeight
  Object.defineProperty(messagesContainer, 'scrollHeight', { configurable: true, value: 500 });
  Object.defineProperty(messagesContainer, 'scrollTop', { configurable: true, value: 0, writable: true });
  
  // Add a message
  mrBloomStore.update(s => ({ 
    ...s, 
    chatHistory: [{ id: '1', role: 'user', content: 'Test', timestamp: '' }] 
  }));
  
  // Auto-scroll relies on tick() inside the component
  await tick();
  
  await waitFor(() => {
    expect(messagesContainer.scrollTop).toBe(500);
  });
});
