import { describe, expect, it } from 'vitest';
import { resolveSeason } from './season';
import { SceneSeason } from '$lib/types/weather';

describe('resolveSeason', () => {
  it.each(['SPRING', 'SUMMER', 'AUTUMN', 'WINTER'] as const)('honors manual %s', (season) => {
    expect(resolveSeason(season, 0, -45)).toBe(season);
  });
  it.each([
    [0, 'WINTER', 'SUMMER'],
    [1, 'WINTER', 'SUMMER'],
    [2, 'SPRING', 'AUTUMN'],
    [3, 'SPRING', 'AUTUMN'],
    [4, 'SPRING', 'AUTUMN'],
    [5, 'SUMMER', 'WINTER'],
    [6, 'SUMMER', 'WINTER'],
    [7, 'SUMMER', 'WINTER'],
    [8, 'AUTUMN', 'SPRING'],
    [9, 'AUTUMN', 'SPRING'],
    [10, 'AUTUMN', 'SPRING'],
    [11, 'WINTER', 'SUMMER'],
  ] as const)('maps month %i across both hemispheres', (month, north, south) => {
    expect(resolveSeason('AUTO', month, 20)).toBe(north);
    expect(resolveSeason('AUTO', month, -20)).toBe(south);
    expect(resolveSeason('AUTO', month, 0)).toBe(north);
    expect(resolveSeason('AUTO', month, null)).toBe(north);
  });
});
