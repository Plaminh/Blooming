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
    gap: 18px;
    margin-bottom: 12px;
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
    width: 148px;
    flex-shrink: 0;
  }
  
  .name {
    font-family: var(--bloom-body-font);
    font-weight: 700;
    color: #064798;
    font-size: 18px;
    font-weight: 500;
    line-height: 1.2;
    text-align: center;
  }

  .initial .name {
    margin-top: 10px;
  }
  
  .time {
    font-family: var(--bloom-body-font);
    color: #92b9d4;
    font-size: 11px;
  }
  
  .bubble {
    background: #f1f9ff;
    border: 2px solid #91c9ee;
    padding: 20px 22px;
    border-radius: 7px;
    font-family: var(--bloom-body-font);
    font-size: 23px;
    color: #071f66;
    line-height: 1.4;
    position: relative;
    max-width: 80%;
  }
  
  .assistant .bubble {
    border-top-left-radius: 7px;
  }
  
  .assistant .bubble::before {
    content: '';
    position: absolute;
    top: 62px;
    left: -19px;
    width: 0;
    height: 0;
    border-top: 12px solid #91c9ee;
    border-left: 18px solid transparent;
  }
  
  .assistant .bubble::after {
    content: '';
    position: absolute;
    top: 60px;
    left: -14px;
    width: 0;
    height: 0;
    border-top: 9px solid #f1f9ff;
    border-left: 14px solid transparent;
  }

  .assistant.initial .bubble {
    width: 389px;
    height: 86px;
    min-height: 86px;
    margin-top: 35px;
    padding-block: 0;
    box-sizing: border-box;
    display: flex;
    align-items: center;
  }
  
  .user .bubble {
    background: #e1f5ff;
    border-color: #a9e0f5;
    border-bottom-right-radius: 0;
    position: relative;
    padding-bottom: 24px; /* Space for time */
  }
  
  .user .bubble::before {
    content: '';
    position: absolute;
    bottom: -1px;
    right: -8px;
    width: 0;
    height: 0;
    border-bottom: 8px solid #a9e0f5;
    border-right: 8px solid transparent;
  }
  
  .user .bubble::after {
    content: '';
    position: absolute;
    bottom: 0px;
    right: -6px;
    width: 0;
    height: 0;
    border-bottom: 6px solid #e1f5ff;
    border-right: 6px solid transparent;
  }
  
  .user-time {
    position: absolute;
    bottom: 8px;
    right: 12px;
  }
</style>
