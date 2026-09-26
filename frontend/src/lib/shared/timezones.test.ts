import { describe, expect, it } from 'vitest';
import { normalizeTimezone, supportedTimezones } from './timezones';

describe('supportedTimezones', () => {
  it('uses the complete runtime timezone source across IANA regions', () => {
    const zones = supportedTimezones();
    expect(zones).toContain('Asia/Ho_Chi_Minh');
    expect(zones).toContain('Asia/Tokyo');
    expect(zones).toContain('America/New_York');
    expect(zones).toContain('Europe/London');
    expect(zones).toContain('Australia/Sydney');
    for (const region of ['Africa/', 'America/', 'Antarctica/', 'Asia/', 'Atlantic/', 'Australia/', 'Europe/', 'Indian/', 'Pacific/'])
      expect(zones.some((zone) => zone.startsWith(region))).toBe(true);
  });

  it('normalizes the legacy Vietnam alias', () => {
    expect(normalizeTimezone('Asia/Saigon')).toBe('Asia/Ho_Chi_Minh');
  });
});
