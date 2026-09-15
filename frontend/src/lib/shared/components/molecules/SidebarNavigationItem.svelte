<script lang="ts">
  import AppIcon from '../atoms/AppIcon.svelte';

  let {
    label,
    icon,
    active = false,
    onClick
  }: {
    label: string;
    icon: 'today' | 'goals' | 'chat' | 'settings';
    active?: boolean;
    onClick?: () => void;
  } = $props();
</script>

<button class="nav-item" class:active onclick={onClick} aria-current={active ? 'page' : undefined}>
  <AppIcon name={icon} scale={1.62} />
  <span>{label}</span>
</button>

<style>
  .nav-item {
    display: flex;
    align-items: center;
    width: 100%;
    min-height: 58px;
    gap: 15px;
    padding: 7px 10px;
    border: 1px solid transparent;
    border-radius: 5px;
    background: transparent;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 20px;
    font-weight: 700;
    text-align: left;
    white-space: nowrap;
    cursor: pointer;
  }

  .nav-item:hover {
    background: rgba(189, 230, 248, 0.45);
  }

  .nav-item.active {
    border-color: #caebf4;
    background: #bde6f8;
    color: #06429a;
  }

  .nav-item:focus-visible {
    outline: 2px solid #008ec5;
    outline-offset: -2px;
  }

  .nav-item :global(img.app-icon) {
    transform: scale(1.8);
  }
</style>
