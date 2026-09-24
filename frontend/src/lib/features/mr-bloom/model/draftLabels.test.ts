import { describe, expect, it } from 'vitest';
import { clockOf, dayLabel, recurrenceLabel } from './draftLabels';

describe('draft labels', () => {
  it('reads the wall-clock time of server ISO datetimes', () => {
    expect(clockOf('2026-09-28T19:00:00+07:00')).toBe('19:00');
    expect(clockOf('2026-09-28T07:30:00Z')).toBe('07:30');
    expect(clockOf('09:15')).toBe('09:15');
    expect(clockOf(null)).toBe('');
  });

  it('describes repetition', () => {
    expect(recurrenceLabel({ freq: 'DAILY' })).toBe('Repeats daily');
    expect(recurrenceLabel({ freq: 'WEEKLY', weekdays: [0, 2] })).toBe('Repeats weekly · Mon, Wed');
    expect(recurrenceLabel({ freq: 'DAILY', until: '2026-09-27' })).toBe('Repeats daily until Sun 27/09');
    expect(recurrenceLabel(null)).toBeNull();
  });

  it('labels a date without a timezone shift', () => {
    expect(dayLabel('2026-09-28')).toBe('Mon 28/09');
    expect(dayLabel('2026-01-01')).toBe('Thu 01/01');
  });
});
