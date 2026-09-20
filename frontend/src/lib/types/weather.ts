export enum WeatherCondition {
  CLEAR = 'CLEAR',
  CLOUDY = 'CLOUDY',
  OVERCAST = 'OVERCAST',
  RAIN = 'RAIN',
  THUNDERSTORM = 'THUNDERSTORM'
}

export enum WeatherStatus {
  OK = 'OK',
  STALE = 'STALE',
  UNAVAILABLE = 'UNAVAILABLE',
  DISABLED = 'DISABLED'
}

export enum SceneSeason {
  AUTO = 'AUTO',
  SPRING = 'SPRING',
  SUMMER = 'SUMMER',
  AUTUMN = 'AUTUMN',
  WINTER = 'WINTER'
}

export interface PlaceCandidate {
  name: string;
  lat: number;
  lon: number;
}

export interface PlaceSearchResponse {
  candidates: PlaceCandidate[];
}

export interface WeatherResponse {
  condition: WeatherCondition;
  status: WeatherStatus;
  updated_at: string | null;
}
