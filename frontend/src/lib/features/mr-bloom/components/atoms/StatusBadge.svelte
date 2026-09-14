<script lang="ts">
  let { status }: { status: 'Core' | 'Optional' } = $props();
</script>

<div class="status-badge {status.toLowerCase()}">
  {status}
</div>

<style>
  .status-badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: var(--bloom-body-font);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
  }
  
  .core {
    background: #e1f5ff;
    color: #064798;
    border: 1px solid #a9e0f5;
  }
  
  .optional {
    background: #fdfaf3;
    color: #92b9d4;
    border: 1px solid #cfc9b9;
  }
</style>
