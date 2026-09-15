<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  let { onEdit, onReplan }: { onEdit: () => void; onReplan: () => void } = $props();
</script>

<footer class="bottom-actions">
  <button class="action edit" onclick={onEdit}>
    <AppIcon name="pencil" scale={0.7} />
    <span>EDIT MANUALLY</span>
  </button>
  <button class="action replan" onclick={onReplan}>
    <AppIcon name="replan" scale={0.7} />
    <span>REPLAN WITH MR. BLOOM</span>
  </button>
</footer>

<style>
  .bottom-actions {
    display: flex;
    height: 82px;
    flex: 0 0 82px;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    padding: 12px 14px;
  }
  .action {
    display: flex;
    height: 55px;
    align-items: center;
    justify-content: center;
    gap: 9px;
    padding: 0 18px;
    border: 1px solid #aaa79f;
    border-radius: 4px;
    background: var(--bloom-action-secondary-bg);
    color: #074a88;
    font-family: var(--bloom-body-font);
    font-size: 16px;
    font-weight: 700;
    white-space: nowrap;
    cursor: pointer;
  }
  .edit { width: 210px; }
  .replan {
    width: 264px;
    border-color: #177d4d;
    background: var(--bloom-action-primary-bg);
    color: #eff9ee;
  }
  .action:hover { filter: brightness(1.04); }
  .action:focus-visible { outline: 2px solid #00aeea; outline-offset: 2px; }
</style>
