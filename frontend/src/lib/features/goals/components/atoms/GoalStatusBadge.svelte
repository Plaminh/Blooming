<script lang="ts">
  import type { MilestoneStatus } from '../../models';

  let { status }: { status: MilestoneStatus } = $props();

  let badgeClass = $derived.by(() => {
    switch (status) {
      case 'Completed': return 'status-completed';
      case 'In progress': return 'status-in-progress';
      case 'Not started': return 'status-not-started';
      default: return '';
    }
  });
</script>

<span class="badge {badgeClass}">
  {status}
</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 4px;
    font-family: var(--bloom-body-font);
    font-size: 13px;
    font-weight: 500;
  }
  .status-completed {
    background: #4e9d67;
    color: white;
  }
  .status-in-progress {
    background: #e4f4ed;
    color: #438f61;
  }
  .status-not-started {
    background: #e5edf5;
    color: #557fa6;
  }
</style>
