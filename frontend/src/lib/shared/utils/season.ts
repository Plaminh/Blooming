import { SceneSeason } from '$lib/types/weather';

export function resolveSeason(value: string, month: number, latitude: number | null): SceneSeason {
  if (value !== SceneSeason.AUTO && Object.values(SceneSeason).includes(value as SceneSeason)) {
    return value as SceneSeason;
  }
  const north = month >= 2 && month <= 4 ? SceneSeason.SPRING
    : month >= 5 && month <= 7 ? SceneSeason.SUMMER
    : month >= 8 && month <= 10 ? SceneSeason.AUTUMN
    : SceneSeason.WINTER;
  if (latitude === null || latitude >= 0) return north;
  return {
    [SceneSeason.SPRING]: SceneSeason.AUTUMN,
    [SceneSeason.SUMMER]: SceneSeason.WINTER,
    [SceneSeason.AUTUMN]: SceneSeason.SPRING,
    [SceneSeason.WINTER]: SceneSeason.SUMMER,
  }[north];
}
