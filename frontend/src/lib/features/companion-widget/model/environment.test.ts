import { describe, it, expect } from 'vitest';
import { datePartsInTimezone, getDaytimeFromHour, getSeasonFromMonth } from './environment';

describe('environment helpers', () => {
  it('uses the configured timezone across date boundaries', () => {
    const instant = new Date('2026-03-01T00:30:00Z');
    expect(datePartsInTimezone(instant, 'America/Los_Angeles')).toEqual({ hour: 16, month: 1 });
    expect(datePartsInTimezone(instant, 'Asia/Ho_Chi_Minh')).toEqual({ hour: 7, month: 2 });
  });
  describe('getDaytimeFromHour', () => {
    it('returns NIGHT for early morning (4)', () => {
      expect(getDaytimeFromHour(4)).toBe('NIGHT');
    });

    it('returns DAWN for dawn (5)', () => {
      expect(getDaytimeFromHour(5)).toBe('DAWN');
    });

    it('returns MORNING for morning (7)', () => {
      expect(getDaytimeFromHour(7)).toBe('MORNING');
    });

    it('returns NOON for noon (11)', () => {
      expect(getDaytimeFromHour(11)).toBe('NOON');
    });

    it('returns AFTERNOON for afternoon (14)', () => {
      expect(getDaytimeFromHour(14)).toBe('AFTERNOON');
    });

    it('returns SUNSET for sunset (17)', () => {
      expect(getDaytimeFromHour(17)).toBe('SUNSET');
    });

    it('returns NIGHT for night (20)', () => {
      expect(getDaytimeFromHour(20)).toBe('NIGHT');
    });
  });

  describe('getSeasonFromMonth', () => {
    it('returns SPRING for March (2)', () => {
      expect(getSeasonFromMonth(2)).toBe('SPRING');
    });

    it('returns SUMMER for June (5)', () => {
      expect(getSeasonFromMonth(5)).toBe('SUMMER');
    });

    it('returns AUTUMN for September (8)', () => {
      expect(getSeasonFromMonth(8)).toBe('AUTUMN');
    });

    it('returns WINTER for December (11)', () => {
      expect(getSeasonFromMonth(11)).toBe('WINTER');
    });
  });
});
