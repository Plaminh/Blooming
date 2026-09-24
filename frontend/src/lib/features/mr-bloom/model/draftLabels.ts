import type { RecurrenceDraft } from '$lib/api';

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

/**
 * The wall-clock "HH:MM" of a draft time.
 *
 * The server sends fixed times and deadlines as ISO datetimes carrying the
 * draft's own UTC offset ("2026-09-28T19:00:00+07:00"), so the local time is
 * the text after "T". Plain "HH:MM" values (typed by the user) pass through.
 */
export function clockOf(value: string | null | undefined): string {
  if (!value) return '';
  const iso = value.match(/T(\d{2}:\d{2})/);
  return iso ? iso[1] : value.slice(0, 5);
}

export function recurrenceLabel(rule: RecurrenceDraft | null | undefined): string | null {
  if (!rule) return null;
  const days = rule.weekdays ?? [];
  let text = rule.freq === 'DAILY'
    ? 'Repeats daily'
    : days.length
      ? `Repeats weekly · ${days.map(day => WEEKDAYS[day] ?? '?').join(', ')}`
      : 'Repeats weekly';
  if (rule.until) text += ` until ${dayLabel(rule.until)}`;
  return text;
}

/** "Mon 28/09" for an ISO date, without shifting it through UTC. */
export function dayLabel(isoDate: string): string {
  const [year, month, day] = isoDate.split('-').map(Number);
  if (!year || !month || !day) return isoDate;
  const weekday = new Date(Date.UTC(year, month - 1, day)).getUTCDay();
  return `${WEEKDAYS[(weekday + 6) % 7]} ${String(day).padStart(2, '0')}/${String(month).padStart(2, '0')}`;
}
