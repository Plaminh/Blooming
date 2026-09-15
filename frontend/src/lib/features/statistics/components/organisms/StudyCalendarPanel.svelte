<script lang="ts">
  import CalendarDayCell from '../atoms/CalendarDayCell.svelte';
  import CalendarMonthNav from '../molecules/CalendarMonthNav.svelte';
  import CalendarLegend from '../molecules/CalendarLegend.svelte';
  import type { CalendarDayState } from '../../types';

  let { studiedDays = [] }: { studiedDays: CalendarDayState[] } = $props();

  let currentYear = $state(2026);
  let currentMonth = $state(5); // June

  let daysInMonth = $derived(new Date(currentYear, currentMonth + 1, 0).getDate());
  let firstWeekdayOffset = $derived((new Date(currentYear, currentMonth, 1).getDay() + 6) % 7);
  
  let monthLabel = $derived(
    new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(new Date(currentYear, currentMonth))
  );

  function nextMonth() {
    if (currentMonth === 11) {
      currentMonth = 0;
      currentYear++;
    } else {
      currentMonth++;
    }
  }

  function prevMonth() {
    if (currentMonth === 0) {
      currentMonth = 11;
      currentYear--;
    } else {
      currentMonth--;
    }
  }

  const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
</script>

<div class="study-calendar-panel">
  <div class="panel-header">
    <h2>STUDY CALENDAR</h2>
    <CalendarMonthNav {monthLabel} onPrev={prevMonth} onNext={nextMonth} />
  </div>

  <div class="calendar-grid">
    {#each WEEKDAYS as weekday}
      <div class="weekday-header">{weekday}</div>
    {/each}

    {#each Array(firstWeekdayOffset) as _}
      <CalendarDayCell day={0} state="empty" />
    {/each}

    {#each Array(daysInMonth) as _, i}
      {@const day = i + 1}
      {@const record = studiedDays.find(d => d.day === day)}
      {@const state = record ? record.status : 'no-record'}
      <CalendarDayCell {day} {state} />
    {/each}

    {#each Array(42 - daysInMonth - firstWeekdayOffset) as _}
      <CalendarDayCell day={0} state="empty" />
    {/each}
  </div>

  <div class="panel-footer">
    <CalendarLegend />
  </div>
</div>

<style>
  .study-calendar-panel {
    background: var(--color-surface);
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 8px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-width: 0;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  h2 {
    margin: 0;
    font-family: var(--bloom-display-font);
    font-size: var(--bloom-panel-title-size);
    font-weight: var(--bloom-panel-title-weight);
    letter-spacing: var(--bloom-panel-title-tracking);
    line-height: var(--bloom-panel-title-line-height);
    color: var(--bloom-text-dark-blue);
  }

  .calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
    justify-items: center;
  }

  .weekday-header {
    font-family: var(--bloom-body-font);
    font-size: 12px;
    font-weight: 700;
    color: var(--bloom-text-muted-blue);
    text-align: center;
    padding-bottom: 8px;
  }

  .panel-footer {
    display: flex;
    justify-content: flex-end;
    margin-top: 8px;
  }
</style>
