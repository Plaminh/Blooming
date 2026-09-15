<script lang="ts">
  import AppIcon, { type IconName } from '$lib/shared/components/atoms/AppIcon.svelte';

  let { 
    icon, 
    title, 
    description,
    selected = false,
    onclick
  }: { 
    icon: IconName; 
    title: string; 
    description: string;
    selected?: boolean;
    onclick: () => void;
  } = $props();
</script>

<button
  class="prompt-suggestion"
  class:selected
  aria-pressed={selected}
  {onclick}
>
  <div class="icon-container">
    <AppIcon name={icon} size="detail" />
  </div>
  <div class="content">
    <div class="title">{title}</div>
    <div class="description">{description}</div>
  </div>
  <div class="arrow">
    <AppIcon name="chevron-right" size="control" />
  </div>
</button>

<style>
  .prompt-suggestion {
    display: flex;
    align-items: center;
    width: 100%;
    min-height: 88px;
    background: rgba(255, 253, 247, 0.7);
    border: 2px solid #c9c3b5;
    border-radius: 7px;
    padding: 10px 18px 10px 14px;
    cursor: pointer;
    text-align: left;
    transition: background-color 0.15s ease;
  }
  
  .prompt-suggestion:hover {
    background: #eef8fd;
  }

  .prompt-suggestion.selected {
    border-color: #559fd0;
    background: #e6f6ff;
  }
  
  .icon-container {
    width: 32px;
    height: 32px;
    flex: 0 0 32px;
    display: grid;
    place-items: center;
    margin-right: 12px;
    color: #0b506e;
    box-sizing: border-box;
  }

  .content {
    flex: 1;
    min-width: 0;
  }
  
  .title {
    font-family: var(--bloom-display-font);
    font-size: 19px;
    font-weight: 800;
    line-height: 1.25;
    letter-spacing: -0.055em;
    color: #071f66;
    margin-bottom: 2px;
    text-transform: uppercase;
  }
  
  .description {
    font-family: var(--bloom-body-font);
    font-size: 15px;
    color: #1a6595;
    line-height: 1.35;
  }
  
  .arrow {
    display: grid;
    width: 31px;
    place-items: center;
    color: #071f66;
  }
</style>
