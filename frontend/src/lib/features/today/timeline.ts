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

export function formatTimelineDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (hours === 0) return `${remainingMinutes} min`;
  if (remainingMinutes === 0) return hours === 1 ? '1 hour' : `${hours} h`;
  return `${hours} h ${remainingMinutes} min`;
}
