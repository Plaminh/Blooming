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

test('UI-008, UI-009, UI-012, E2E-010: Message failure and retry lifecycle', async () => {
  let rejectApi: (err: any) => void;
  let resolveApi: (val: any) => void;
  
  // First request will fail
  const apiPromise1 = new Promise((resolve, reject) => {
    rejectApi = reject;
  });
  vi.mocked(api.post).mockReturnValueOnce(apiPromise1);
  
  const { getByPlaceholderText, getAllByText, getByRole, queryByRole } = render(MrBloomConversationPanel);
  const input = getByPlaceholderText(/Choose what you want to plan first/i);
  
  // Send message
  await fireEvent.input(input, { target: { value: 'Hello Fail' } });
  await fireEvent.keyDown(input, { key: 'Enter' });
  
  expect(api.post).toHaveBeenCalledTimes(1);
  
  // E2E-010: Provider timeout/failure occurs
  rejectApi!(new Error('Network/Timeout error'));
  
  await waitFor(() => {
    // Waiting state ends
    expect(queryByRole('status', { name: /waiting for response/i })).not.toBeInTheDocument();
  });
  
  // UI-008: Message remains and is marked failed
  expect(getAllByText('Hello Fail')).toHaveLength(1);
  const retryBtn = getByRole('button', { name: /Gửi lại|Retry/i }); 
  expect(retryBtn).toBeInTheDocument();
  
  // Prepare for retry
  const apiPromise2 = new Promise(resolve => {
    resolveApi = resolve;
  });
  vi.mocked(api.post).mockReturnValueOnce(apiPromise2);
  
  // UI-009, UI-012: Retry failed message
  await fireEvent.click(retryBtn);
  
  // API called again
  expect(api.post).toHaveBeenCalledTimes(2);
  
  // Failure marker disappears, it's pending again
  expect(queryByRole('button', { name: /Gửi lại|Retry/i })).not.toBeInTheDocument();
  expect(queryByRole('status', { name: /waiting for response/i })).toBeInTheDocument();
  
  // Resolve the retry request
  resolveApi!({ reply: 'Recovered', draft: null });
  
  await waitFor(() => {
    expect(queryByRole('status', { name: /waiting for response/i })).not.toBeInTheDocument();
  });
  
  // User message remains exactly ONE logical turn (no duplicate)
  expect(getAllByText('Hello Fail')).toHaveLength(1);
  expect(getAllByText('Recovered')).toHaveLength(1);
});

test('UI-010: Double-click Send protection', async () => {
  let resolveApi: (val: any) => void;
  // A request that hangs so we can double click
  vi.mocked(api.post).mockReturnValue(new Promise((resolve) => { resolveApi = resolve; }));
  
  const { getByPlaceholderText, getByRole, getAllByText, queryByRole } = render(MrBloomConversationPanel);
  const input = getByPlaceholderText(/Choose what you want to plan first/i);
  const sendButton = getByRole('button', { name: 'Send' });
  
  await fireEvent.input(input, { target: { value: 'Rapid click' } });
  
  // Double click! 
  await fireEvent.click(sendButton);
  await fireEvent.click(sendButton); // second click while waiting
  
  // Should only invoke API once due to isWaitingForResponse guard
  expect(api.post).toHaveBeenCalledTimes(1);
  
  // Should only create ONE user message
  expect(getAllByText('Rapid click')).toHaveLength(1);
  
  // Resolve the first (and only) request
  resolveApi!({ reply: 'I am here', draft: null });
  
  await waitFor(() => {
    // Waiting state must become false
    expect(queryByRole('status', { name: /waiting for response/i })).not.toBeInTheDocument();
  });
  
  // Assistant response must appear
  expect(getAllByText('I am here')).toHaveLength(1);
});


test('UI-014: send_text quick reply uses normal submitMessage flow', async () => {
  const { getByText } = render(MrBloomConversationPanel);
  mrBloomStore.update(state => ({
    ...state,
    suggestions: [{ label: 'Just do it', send_text: 'I said just do it' }]
  }));
  await tick();
  
  vi.mocked(api.post).mockResolvedValueOnce({ reply: 'Done', draft: null });
  
  const button = getByText('Just do it');
  await fireEvent.click(button);
  
  expect(api.post).toHaveBeenCalledWith('/assistant/chat', expect.objectContaining({
    message: 'I said just do it'
  }));
  
  expect(get(mrBloomStore).chatHistory.at(-2)?.content).toBe('I said just do it');
  expect(get(mrBloomStore).chatHistory.at(-2)?.role).toBe('user');
});

test('UI-015: patch quick reply invokes applyPatch without calling chat endpoint', async () => {
  const { getByText } = render(MrBloomConversationPanel);
  const patchOp = { op: 'remove_task', task_id: '1' };
  
  mrBloomStore.update(state => ({
    ...state,
    activeDraft: { type: 'today', planDate: '2026-01-01', timezone: 'UTC', windows: [], tasks: [] },
    suggestions: [{ label: 'Remove task', patch: [patchOp] }]
  }));
  await tick();
  
  vi.mocked(api.post).mockResolvedValueOnce({ draft: { type: 'today', tasks: [] }, preview: null });
  
  const button = getByText('Remove task');
  await fireEvent.click(button);
  
  expect(api.post).toHaveBeenCalledWith('/assistant/apply-patch', expect.objectContaining({
    ops: [patchOp]
  }));
  expect(api.post).not.toHaveBeenCalledWith('/assistant/chat', expect.anything());
});

test('UI-016 / UI-017: action executes only after explicit user click', async () => {
  const { getByText, getByPlaceholderText } = render(MrBloomConversationPanel);
  const input = getByPlaceholderText(/Choose what you want to plan first/i);
  
  // Stage 1: Submit normal message
  vi.mocked(api.post).mockResolvedValueOnce({
    reply: 'Here is a suggestion',
    draft: null,
    suggestions: [{ label: 'Skip Optionals', action: 'SKIP_OPTIONAL_TODAY' }]
  });
  
  await fireEvent.input(input, { target: { value: 'What should I do?' } });
  await fireEvent.keyDown(input, { key: 'Enter' });
  
  // Wait for the response and suggestion to render
  await waitFor(() => {
    expect(getByText('Skip Optionals')).toBeInTheDocument();
  });
  
  // Verify the action endpoint has NOT been called yet
  expect(api.post).toHaveBeenCalledWith('/assistant/chat', expect.anything());
  expect(api.post).not.toHaveBeenCalledWith('/assistant/actions/SKIP_OPTIONAL_TODAY', expect.anything());
  
  // Stage 2: User explicitly clicks suggestion
  vi.mocked(api.post).mockResolvedValueOnce({});
  const button = getByText('Skip Optionals');
  await fireEvent.click(button);
  
  // Verify the action endpoint is called exactly once
  expect(api.post).toHaveBeenCalledWith('/assistant/actions/SKIP_OPTIONAL_TODAY', expect.anything());
  const actionCalls = vi.mocked(api.post).mock.calls.filter(call => call[0] === '/assistant/actions/SKIP_OPTIONAL_TODAY');
  expect(actionCalls.length).toBe(1);
});

test('UI-018: quick replies are disabled while waiting for response', async () => {
  const { getByText } = render(MrBloomConversationPanel);
  
  mrBloomStore.update(state => ({
    ...state,
    suggestions: [{ label: 'Say hi', send_text: 'hi' }]
  }));
  await tick();
  
  const button = getByText('Say hi') as HTMLButtonElement;
  expect(button.disabled).toBe(false);
  
  let resolveApi: ((val: any) => void) | undefined;
  vi.mocked(api.post).mockReturnValueOnce(new Promise(r => { resolveApi = r; }));
  
  await fireEvent.click(button);
  await tick();
  
  expect(button.disabled).toBe(true);
  
  await fireEvent.click(button);
  expect(api.post).toHaveBeenCalledTimes(1);
  
  resolveApi!({ reply: 'hello', draft: null });
  await tick();
  
  await waitFor(() => {
    expect(document.body.contains(button)).toBe(false);
  });
});
