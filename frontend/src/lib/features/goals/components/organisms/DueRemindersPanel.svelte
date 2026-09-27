<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import GoalsPanelHeader from '../atoms/GoalsPanelHeader.svelte';
  import TargetDateLabel from '../atoms/TargetDateLabel.svelte';

  let { reminders, onAction }: { 
    reminders: any[], 
    onAction: (reminderId: string, action: string, newDate?: string) => Promise<void> 
  } = $props();

  let pendingAction = $state<string | null>(null);

  async function handleAction(reminderId: string, action: string, newDate?: string) {
    if (pendingAction) return;
    pendingAction = `${reminderId}-${action}`;
    try {
      await onAction(reminderId, action, newDate);
    } finally {
      pendingAction = null;
    }
  }
</script>

<section class="panel due-reminders">
  <GoalsPanelHeader title="DUE REMINDERS" />
  
  <div class="panel-body">
    {#if reminders.length > 0}
      {#each reminders as reminder}
      <div class="reminder-item">
        <div class="reminder-main">
          <div class="document-icon"><AppIcon name="clock" size="roadmap-milestone" /></div>
          <div class="reminder-info">
            <h3>{reminder.message}</h3>
            <p>Due: {new Date(reminder.due_at).toLocaleDateString()}</p>
          </div>
        </div>
        <div class="reminder-actions">
          <button disabled={!!pendingAction} onclick={() => handleAction(reminder.id, 'CREATE_PLAN')}>Create Plan</button>
          <button disabled={!!pendingAction} onclick={() => handleAction(reminder.id, 'MARK_COMPLETED')}>Mark Completed</button>
          <button disabled={!!pendingAction} onclick={() => {
              const d = prompt("Move target date (YYYY-MM-DD):", reminder.due_at.substring(0, 10));
              if (d) handleAction(reminder.id, 'MOVE_MILESTONE', new Date(d).toISOString());
          }}>Move Milestone</button>
          <button disabled={!!pendingAction} onclick={() => {
              const d = prompt("Remind Later (YYYY-MM-DD):", reminder.due_at.substring(0, 10));
              if (d) handleAction(reminder.id, 'REMIND_LATER', new Date(d).toISOString());
          }}>Remind Later</button>
        </div>
      </div>
      {/each}
    {:else}
      <p class="empty-state">No due reminders.</p>
    {/if}
  </div>
</section>

<style>
  .panel {
    min-height: 184px;
    background: #fffdf8;
    border: 1px solid #24788c;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    margin-bottom: 10px;
  }
  .panel-body {
    padding: 13px 12px 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 15px;
    overflow-y: auto;
  }
  .reminder-item {
    display: flex;
    flex-direction: column;
    gap: 10px;
    border-bottom: 1px dashed #aab6aa;
    padding-bottom: 10px;
  }
  .reminder-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }
  .reminder-main {
    display: flex;
    align-items: flex-start;
    gap: 14px;
  }
  .document-icon {
    display: grid;
    width: var(--bloom-icon-roadmap-milestone);
    height: var(--bloom-icon-roadmap-milestone);
    flex: 0 0 var(--bloom-icon-roadmap-milestone);
    align-self: center;
    place-items: center;
    color: #e63946;
  }
  .reminder-info {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }
  .reminder-info h3 {
    margin: 0;
    color: #064b91;
    font-family: var(--bloom-display-font);
    font-size: 16px;
    font-weight: 800;
  }
  .reminder-info p {
    margin: 0;
    color: #e63946;
    font-size: 14px;
    font-weight: 600;
  }
  .reminder-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }
  .reminder-actions button {
    background: #c3e5f5;
    border: 1px solid #24788c;
    color: #064b91;
    border-radius: 4px;
    padding: 4px 8px;
    cursor: pointer;
    font-size: 12px;
    font-weight: bold;
  }
  .reminder-actions button:hover {
    background: #a8d5e8;
  }
  .empty-state {
    color: #1479ab;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    margin: 0;
  }
</style>
