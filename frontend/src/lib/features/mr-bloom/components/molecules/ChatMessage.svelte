<script lang="ts">
  import type { ChatMessage as ChatMessageType } from '../../stores/mrBloomStore';
  import ChatAvatar from '../atoms/ChatAvatar.svelte';
  
  let { message }: { message: ChatMessageType } = $props();
</script>

<div class="chat-message {message.role}" class:initial={message.id === '1'}>
  {#if message.role === 'assistant'}
    <div class="avatar-container">
      <ChatAvatar />
      <span class="name">Mr. Bloom</span>
      {#if message.id !== '1'}
        <span class="time">{message.timestamp}</span>
      {/if}
    </div>
  {/if}
  
  <div class="bubble">
    {message.content}
    {#if message.role === 'user'}
      <span class="time user-time">{message.timestamp}</span>
    {/if}
  </div>
</div>

<style>
  .chat-message {
    display: flex;
    gap: 12px;
    width: 100%;
  }
  
  .chat-message.user {
    justify-content: flex-end;
  }
  
  .avatar-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1px;
    width: var(--bloom-chat-avatar-slot);
    flex-shrink: 0;
  }
  
  .name {
    font-family: var(--bloom-body-font);
    font-weight: 700;
    color: #064798;
    font-size: 16px;
    font-weight: 500;
    line-height: 1.2;
    text-align: center;
  }

  .initial .name {
    margin-top: 6px;
  }
  
  .time {
    font-family: var(--bloom-body-font);
    color: #92b9d4;
    font-size: 11px;
  }
  
  .bubble {
    background: var(--bloom-chat-msg-bg);
    border: 2px solid var(--bloom-chat-msg-border);
    padding: 14px 16px;
    border-radius: 7px;
    font-family: var(--bloom-body-font);
    font-size: 18px;
    color: var(--bloom-text-dark-blue);
    line-height: 1.4;
    position: relative;
    max-width: 80%;
    display: flex;
    flex-direction: column;
    overflow-wrap: break-word;
    word-break: break-word;
    white-space: pre-wrap;
  }
  
  .assistant .bubble {
    border-top-left-radius: 7px;
  }
  
  .assistant .bubble::before {
    content: '';
    position: absolute;
    top: 31px;
    left: -19px;
    width: 0;
    height: 0;
    border-top: 12px solid var(--bloom-chat-msg-border);
    border-left: 18px solid transparent;
  }
  
  .assistant .bubble::after {
    content: '';
    position: absolute;
    top: 29px;
    left: -14px;
    width: 0;
    height: 0;
    border-top: 9px solid var(--bloom-chat-msg-bg);
    border-left: 14px solid transparent;
  }

  .assistant.initial .bubble {
    width: 360px;
    margin-top: 8px;
  }
  
  .user .bubble {
    background: var(--bloom-chat-msg-user-bg);
    border-color: var(--bloom-chat-msg-user-border);
    border-bottom-right-radius: 0;
    position: relative;
  }
  
  .user .bubble::before {
    content: '';
    position: absolute;
    bottom: -1px;
    right: -8px;
    width: 0;
    height: 0;
    border-bottom: 8px solid var(--bloom-chat-msg-user-border);
    border-right: 8px solid transparent;
  }
  
  .user .bubble::after {
    content: '';
    position: absolute;
    bottom: 0px;
    right: -6px;
    width: 0;
    height: 0;
    border-bottom: 6px solid var(--bloom-chat-msg-user-bg);
    border-right: 6px solid transparent;
  }
  
  .user-time {
    align-self: flex-end;
    margin-top: 4px;
    color: #9b6076;
  }
</style>
