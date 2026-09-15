<script lang="ts">
  let {
    title,
    id
  }: {
    title: string;
    id?: string;
  } = $props();
</script>

<header class="goals-panel-header">
  <h2 {id}>{title}</h2>
</header>

<style>
  .goals-panel-header {
    display: flex;
    height: 39px;
    flex: 0 0 39px;
    align-items: center;
    gap: 8px;
    padding: 0 14px;
    border-bottom: 1px solid #0c6178;
    background: var(--bloom-titlebar-bg);
    color: #f7fff9;
  }

  h2 {
    margin: 0;
    font-family: var(--bloom-display-font);
    font-size: var(--bloom-panel-title-size);
    font-weight: var(--bloom-panel-title-weight);
    letter-spacing: var(--bloom-panel-title-tracking);
    line-height: var(--bloom-panel-title-line-height);
  }
</style>
