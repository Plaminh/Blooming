import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render } from '@testing-library/svelte';
import ChatMessage from './ChatMessage.svelte';
import source from './ChatMessage.svelte?raw';

// Apply the actual component CSS for rule assertions. JSDOM does not measure layout.
let stylesheet: HTMLStyleElement;
beforeEach(() => {
  stylesheet = document.createElement('style');
  stylesheet.textContent = source.split('<style>')[1].split('</style>')[0];
  document.head.append(stylesheet);
});
afterEach(() => stylesheet.remove());

const assistantMsg = { id: '2', role: 'assistant' as const, content: 'Hello, how can I help?', timestamp: '10:00' };
const userMsg = { id: '3', role: 'user' as const, content: 'Plan my day.', timestamp: '10:01' };

describe('ChatMessage', () => {
  it('renders a short assistant message with avatar, name and timestamp', () => {
    const { container, getByText } = render(ChatMessage, { message: assistantMsg });
    expect(container.querySelector('.chat-message.assistant .bubble')).toHaveTextContent(assistantMsg.content);
    expect(container.querySelector('.avatar-container')).toContainElement(getByText('Mr. Bloom'));
    expect(getByText('10:00')).toBeInTheDocument();
  });

  it('renders a short user message aligned right without an avatar', () => {
    const { container } = render(ChatMessage, { message: userMsg });
    const wrapper = container.querySelector('.chat-message.user')!;
    expect(wrapper.querySelector('.bubble')).toHaveTextContent(userMsg.content);
    expect(getComputedStyle(wrapper).justifyContent).toBe('flex-end');
    expect(container.querySelector('.avatar-container')).toBeNull();
  });

  it.each(['assistant', 'user'] as const)('retains newline characters in multiline %s content', (role) => {
    const content = 'First line\nSecond line\n\nFinal paragraph';
    const { container } = render(ChatMessage, { message: { ...userMsg, role, content } });
    expect(container.querySelector('.bubble')?.textContent).toContain(content);
  });

  it.each(['assistant', 'user'] as const)('renders all long %s content with wrapping rules', (role) => {
    const content = 'A longer planning message. '.repeat(150) + 'unbroken'.repeat(100);
    const { container } = render(ChatMessage, { message: { ...userMsg, role, content } });
    const bubble = container.querySelector('.bubble')!;
    expect(bubble.textContent).toContain(content);
    const style = getComputedStyle(bubble);
    expect(style.overflowWrap).toBe('break-word');
    expect(style.wordBreak).toBe('break-word');
    expect(style.whiteSpace).not.toBe('nowrap');
    expect(style.textOverflow).not.toBe('ellipsis');
  });

  it('keeps the user timestamp after the message in the normal bubble content flow', () => {
    const { container, getByText } = render(ChatMessage, { message: userMsg });
    const bubble = container.querySelector('.bubble')!;
    const time = getByText(userMsg.timestamp);
    expect(time.parentElement).toBe(bubble);
    expect(bubble.lastElementChild).toBe(time);
    expect(bubble.firstChild?.textContent).toContain(userMsg.content);
    expect(getComputedStyle(bubble).display).toBe('flex');
    expect(getComputedStyle(bubble).flexDirection).toBe('column');
    expect(['', 'static', 'relative']).toContain(getComputedStyle(time).position);
    expect(getComputedStyle(time).alignSelf).toBe('flex-end');
  });

  it.each([assistantMsg, userMsg, { ...assistantMsg, id: '1' }])('does not constrain bubble height for $role message $id', (message) => {
    const { container } = render(ChatMessage, { message });
    const style = getComputedStyle(container.querySelector('.bubble')!);
    expect(['', 'auto']).toContain(style.height);
    expect(['', 'auto', '0px']).toContain(style.minHeight);
  });
});
