<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { onRefine }: { onRefine: () => void; } = $props();
</script>

<div class="action-group">
  <button class="btn-action primary" onclick={onRefine}>
    <AppIcon name="play" scale={1.25} />
    ADJUST WITH MR. BLOOM
  </button>
</div>

<style>
  .action-group {
    display: flex;
    height: 56px;
    gap: 8px;
  }
  .btn-action {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    background: #fffdf8;
    border: 1px solid #bdb5a5;
    border-radius: 5px;
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: -0.055em;
    padding: 7px;
    cursor: pointer;
    transition: background 0.1s;
    white-space: nowrap;
  }
  .primary {
    border-color: #247b4c;
    background: var(--bloom-action-primary-bg);
    color: white;
  }
  .primary:hover { background: #3a9e5e; }
</style>
