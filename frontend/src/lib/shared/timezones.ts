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
  const intl = Intl as typeof Intl & { supportedValuesOf?: (key: 'timeZone') => string[] };
  const values = intl.supportedValuesOf?.('timeZone') ?? timeZonesNames;
  return [...new Set(['UTC', ...values.map(normalizeTimezone)])].sort();
}
import { timeZonesNames } from '@vvo/tzdb';
