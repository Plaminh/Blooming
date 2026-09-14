<script lang="ts">
  let { onEdit, onRefine }: { onEdit: () => void; onRefine: () => void; } = $props();
</script>

<div class="action-group">
  <button class="btn-action" onclick={onEdit}>
    EDIT MANUALLY
  </button>
  <button class="btn-action" onclick={onRefine}>
    REFINE WITH MR. BLOOM
  </button>
</div>

<style>
  .action-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 24px;
  }
  .btn-action {
    width: 100%;
    background: #fffdf8;
    border: 1px solid #20a3be;
    border-radius: 5px;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 700;
    padding: 12px;
    cursor: pointer;
    transition: background 0.1s;
  }
  .btn-action:hover {
    background: #eef8f6;
  }
</style>
