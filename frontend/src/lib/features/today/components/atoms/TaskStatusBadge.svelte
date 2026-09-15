<script lang="ts">
  import type { TaskStatus } from '$lib/features/today/types';
  let { status }: { status: TaskStatus } = $props();
  const text = { 'in-progress': 'In progress', completed: 'Completed', upcoming: 'Upcoming' };
</script>

<span class="badge {status}">{text[status]}</span>

<style>
  .badge {
    display: grid;
    min-width: 112px;
    height: 34px;
    place-items: center;
    border-radius: 5px;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 500;
    white-space: nowrap;
  }
  .in-progress { background: #c8ead8; color: #087846; }
  .completed { background: #d9eed8; color: #167d4a; }
  .upcoming { background: #ece9e2; color: #0750ad; }
</style>
