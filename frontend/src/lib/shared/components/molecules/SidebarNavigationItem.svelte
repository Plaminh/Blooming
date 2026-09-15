<script lang="ts">
  import AppIcon from '../atoms/AppIcon.svelte';

  let {
    label,
    icon,
    active = false,
    onClick
  }: {
    label: string;
    icon: 'today' | 'goals' | 'chat' | 'settings' | 'statistics';
    active?: boolean;
    onClick?: () => void;
  } = $props();
</script>

<button class="nav-item" class:active onclick={onClick} aria-current={active ? 'page' : undefined}>
  <span class="nav-icon">
    <span class="nav-icon-frame"><AppIcon name={icon} size="navigation" /></span>
  </span>
  <span class="nav-label">{label}</span>
</button>

<style>
  .nav-item {
    display: flex;
    align-items: center;
    width: 100%;
    min-height: 56px;
    gap: var(--bloom-navigation-label-gap);
    padding: 7px 5px;
    border: 1px solid transparent;
    border-radius: 5px;
    background: transparent;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: var(--bloom-navigation-label-size);
    line-height: var(--bloom-navigation-label-line-height);
    font-weight: 700;
    text-align: left;
    white-space: nowrap;
    cursor: pointer;
  }

  .nav-item:hover {
    background: rgba(189, 230, 248, 0.45);
  }
  .nav-label { min-width: 0; }

  .nav-item.active {
    border-color: #caebf4;
    background: #bde6f8;
    color: #06429a;
  }

  .nav-item:focus-visible {
    outline: 2px solid #008ec5;
    outline-offset: -2px;
  }

  .nav-icon {
    display: grid;
    width: var(--bloom-icon-navigation-slot);
    height: var(--bloom-icon-navigation-slot);
    flex: 0 0 var(--bloom-icon-navigation-slot);
    place-items: center;
  }
  .nav-icon-frame {
    display: grid;
    width: var(--bloom-icon-navigation-frame);
    height: var(--bloom-icon-navigation-frame);
    place-items: center;
  }
</style>
