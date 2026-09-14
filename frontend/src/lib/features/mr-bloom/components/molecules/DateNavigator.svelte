<script lang="ts">
  import IconButton from '../atoms/IconButton.svelte';
  
  let { date = $bindable('') }: { date: string } = $props();
</script>

<div class="date-navigator">
  <span class="label">TARGET:</span>
  <div class="control">
    <span class="date-value">{date}</span>
    <IconButton icon="edit" label="Edit date" variant="ghost" size="small" />
  </div>
</div>

<style>
  .date-navigator {
    display: inline-flex;
    align-items: center;
    background: #fdfaf3;
    border: 1px solid #cfc9b9;
    border-radius: 4px;
    padding: 4px 8px 4px 12px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    color: #064798;
  }
  
  .label {
    font-weight: 700;
    margin-right: 8px;
  }
  
  .control {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }
</style>
