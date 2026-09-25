export function addMinutesToTime(time: string, minutes: number): string {
  const [hour, minute] = time.split(':').map(Number);
  const total = hour * 60 + minute + minutes;
  return `${Math.floor(total / 60).toString().padStart(2, '0')}:${(total % 60).toString().padStart(2, '0')}`;
}

export function minutesBetween(start: string, end: string): number {
  const [startHour, startMinute] = start.split(':').map(Number);
  const [endHour, endMinute] = end.split(':').map(Number);
  return (endHour * 60 + endMinute) - (startHour * 60 + startMinute);
}

export const TIMELINE_DEFAULT_START = '09:00';
export const TIMELINE_DEFAULT_END = '18:00';
export const TIMELINE_PIXELS_PER_HOUR = 70;
export const TIMELINE_TOP_PADDING = 8;

export interface TimelineGeometry {
  start: string;
  end: string;
  hours: string[];
  height: number;
  topFor: (time: string) => number;
}

function timeToMinutes(time: string): number {
  const [hour, minute] = time.split(':').map(Number);
  return hour * 60 + minute;
}

function minutesToTime(minutes: number): string {
  const bounded = Math.max(0, Math.min(24 * 60, minutes));
  return `${Math.floor(bounded / 60).toString().padStart(2, '0')}:${(bounded % 60).toString().padStart(2, '0')}`;
}

export function timeInTimezone(now: Date, timezone: string): string {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: timezone,
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23'
  }).formatToParts(now);
  const hour = parts.find((part) => part.type === 'hour')?.value ?? '00';
  const minute = parts.find((part) => part.type === 'minute')?.value ?? '00';
  return `${hour}:${minute}`;
}

export function createTimelineGeometry(
  ranges: Array<{ startTime: string; endTime: string }>,
  currentTime?: string,
  defaultStart = TIMELINE_DEFAULT_START,
  defaultEnd = TIMELINE_DEFAULT_END
): TimelineGeometry {
  const starts = ranges.map((range) => timeToMinutes(range.startTime));
  const ends = ranges.map((range) => timeToMinutes(range.endTime));
  const startMinutes = Math.floor(Math.min(timeToMinutes(defaultStart), ...starts) / 60) * 60;
  const currentMinutes = currentTime ? timeToMinutes(currentTime) : Number.NEGATIVE_INFINITY;
  const endMinutes = Math.ceil(
    Math.max(timeToMinutes(defaultEnd), ...ends, currentMinutes, startMinutes + 60) / 60
  ) * 60;
  const duration = endMinutes - startMinutes;
  const topFor = (time: string) => {
    const clamped = Math.max(startMinutes, Math.min(endMinutes, timeToMinutes(time)));
    return TIMELINE_TOP_PADDING + (clamped - startMinutes) * TIMELINE_PIXELS_PER_HOUR / 60;
  };
  const hours = Array.from(
    { length: duration / 60 + 1 },
    (_, index) => minutesToTime(startMinutes + index * 60)
  );
  return {
    start: minutesToTime(startMinutes),
    end: minutesToTime(endMinutes),
    hours,
    height: TIMELINE_TOP_PADDING * 2 + duration * TIMELINE_PIXELS_PER_HOUR / 60,
    topFor
  };
}

export function formatTimelineDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (hours === 0) return `${remainingMinutes} min`;
  if (remainingMinutes === 0) return hours === 1 ? '1 hour' : `${hours} h`;
  return `${hours} h ${remainingMinutes} min`;
}
