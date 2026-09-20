import type { Daytime, Season, Weather } from '$lib/features/companion-widget/model/environment';

const times: Daytime[] = ['DAWN', 'MORNING', 'NOON', 'AFTERNOON', 'SUNSET', 'NIGHT'];
const seasons: Season[] = ['SPRING', 'SUMMER', 'AUTUMN', 'WINTER'];
const weathers: Weather[] = ['CLEAR', 'CLOUDY', 'OVERCAST', 'RAIN', 'THUNDERSTORM'];

export function parseSceneQuery(query: URLSearchParams): {
  daytimeOverride?: Daytime;
  seasonOverride?: Season;
  weatherOverride?: Weather;
} {
  const time = query.get('time') as Daytime;
  const season = query.get('season') as Season;
  const weather = query.get('weather') as Weather;
  return {
    daytimeOverride: times.includes(time) ? time : undefined,
    seasonOverride: seasons.includes(season) ? season : undefined,
    weatherOverride: weathers.includes(weather) ? weather : undefined,
  };
}
