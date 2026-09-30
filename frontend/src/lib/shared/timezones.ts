const TIMEZONE_ALIASES: Record<string, string> = {
  'Asia/Saigon': 'Asia/Ho_Chi_Minh',
  'US/Eastern': 'America/New_York',
  'US/Central': 'America/Chicago',
  'US/Mountain': 'America/Denver',
  'US/Pacific': 'America/Los_Angeles',
};

export function normalizeTimezone(value: string): string {
  const trimmed = value.trim();
  return TIMEZONE_ALIASES[trimmed] ?? trimmed;
}

export function isValidTimezone(value: string): boolean {
  try {
    new Intl.DateTimeFormat('en', { timeZone: normalizeTimezone(value) }).format();
    return true;
  } catch {
    return false;
  }
}

export function supportedTimezones(): string[] {
  return [...new Set(['UTC', ...Intl.supportedValuesOf('timeZone').map(normalizeTimezone)])].sort();
}
