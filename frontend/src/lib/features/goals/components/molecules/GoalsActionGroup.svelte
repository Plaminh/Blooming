<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { onEdit, onRefine }: { onEdit: () => void; onRefine: () => void; } = $props();
</script>

<div class="action-group">
  <button class="btn-action secondary" onclick={onEdit}>
    <AppIcon name="pencil" scale={1.2} />
    EDIT MANUALLY
  </button>
  <button class="btn-action primary" onclick={onRefine}>
    <AppIcon name="play" scale={1.25} />
    REFINE WITH MR. BLOOM
  </button>
</div>

<style>
  .action-group {
    display: grid;
    height: 68px;
    grid-template-columns: 140px minmax(0, 1fr);
    gap: 10px;
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
    padding: 10px;
    cursor: pointer;
    transition: background 0.1s;
    white-space: nowrap;
  }
  .secondary:hover {
    background: #eef8f6;
  }
  .primary {
    border-color: #247b4c;
    background: linear-gradient(180deg, #50ad6a 0%, #32965a 100%);
    color: white;
  }
  .primary:hover { background: #3a9e5e; }
</style>
