<script lang="ts">
  let {
    title,
    id,
    icon = false
  }: {
    title: string;
    id?: string;
    icon?: boolean;
  } = $props();
</script>

<header class="goals-panel-header">
  {#if icon}
    <img src="/assets/widget/icons/leaf-icon.png" alt="" />
  {/if}
  <h2 {id}>{title}</h2>
</header>

<style>
  .goals-panel-header {
    display: flex;
    height: 43px;
    flex: 0 0 43px;
    align-items: center;
    gap: 8px;
    padding: 0 14px;
    border-bottom: 1px solid #0c6178;
    background: linear-gradient(180deg, #3d9caf 0%, #2b8ca4 100%);
    color: #f7fff9;
  }

  img {
    width: 28px;
    height: 30px;
    object-fit: contain;
    image-rendering: pixelated;
    transform: translateX(-4px) scale(1.5);
  }

  h2 {
    margin: 0;
    font-family: var(--bloom-display-font);
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.045em;
    line-height: 1;
  }
</style>
