import dawnImg from '$lib/assets/widget/environment/daytime/dawn.png';
import morningImg from '$lib/assets/widget/environment/daytime/morning.png';
import noonImg from '$lib/assets/widget/environment/daytime/noon.png';
import afternoonImg from '$lib/assets/widget/environment/daytime/afternoon.png';
import sunsetImg from '$lib/assets/widget/environment/daytime/sunset.png';
import nightImg from '$lib/assets/widget/environment/daytime/night.png';

export type Daytime = 'DAWN' | 'MORNING' | 'NOON' | 'AFTERNOON' | 'SUNSET' | 'NIGHT';

export const DAYTIME_ASSETS: Record<Daytime, string> = {
  DAWN: dawnImg,
  MORNING: morningImg,
  NOON: noonImg,
  AFTERNOON: afternoonImg,
  SUNSET: sunsetImg,
  NIGHT: nightImg,
};

// Deterministic daytime from local hour (0-23)
export function getDaytimeFromHour(hour: number): Daytime {
  if (hour >= 5 && hour < 7) return 'DAWN';
  if (hour >= 7 && hour < 11) return 'MORNING';
  if (hour >= 11 && hour < 14) return 'NOON';
  if (hour >= 14 && hour < 17) return 'AFTERNOON';
  if (hour >= 17 && hour < 20) return 'SUNSET';
  return 'NIGHT';
}

import springImg from '$lib/assets/widget/environment/season/spring.png';
import summerImg from '$lib/assets/widget/environment/season/summer.png';
import autumnImg from '$lib/assets/widget/environment/season/autumn.png';
import winterImg from '$lib/assets/widget/environment/season/winter.png';

export type Season = 'SPRING' | 'SUMMER' | 'AUTUMN' | 'WINTER';

export const SEASON_ASSETS: Record<Season, string> = {
  SPRING: springImg,
  SUMMER: summerImg,
  AUTUMN: autumnImg,
  WINTER: winterImg,
};

// Deterministic season from local month (0-11)
export function getSeasonFromMonth(month: number): Season {
  if (month >= 2 && month <= 4) return 'SPRING'; // Mar, Apr, May
  if (month >= 5 && month <= 7) return 'SUMMER'; // Jun, Jul, Aug
  if (month >= 8 && month <= 10) return 'AUTUMN'; // Sep, Oct, Nov
  return 'WINTER'; // Dec, Jan, Feb
}

export function datePartsInTimezone(date: Date, timezone: string): { hour: number; month: number } {
  try {
    const parts = new Intl.DateTimeFormat('en-US', {
      timeZone: timezone,
      hour: 'numeric',
      hourCycle: 'h23',
      month: 'numeric',
    }).formatToParts(date);
    return {
      hour: Number(parts.find((part) => part.type === 'hour')?.value),
      month: Number(parts.find((part) => part.type === 'month')?.value) - 1,
    };
  } catch (error) {
    if (!(error instanceof RangeError)) throw error;
    return { hour: date.getUTCHours(), month: date.getUTCMonth() };
  }
}

import cloudyImg from '$lib/assets/widget/environment/weather/cloudy.png';
import overcastImg from '$lib/assets/widget/environment/weather/overcast.png';
import stormOverlayImg from '$lib/assets/widget/environment/weather/storm-overlay.png';

export type Weather = 'CLEAR' | 'CLOUDY' | 'OVERCAST' | 'RAIN' | 'THUNDERSTORM';

export const WEATHER_ASSETS: Record<Weather, string | null> = {
  CLEAR: null,
  CLOUDY: cloudyImg,
  OVERCAST: overcastImg,
  RAIN: overcastImg, // uses overcast + animated rain
  THUNDERSTORM: stormOverlayImg, // uses storm + denser rain
};

export type RainConfig = {
  streakCount: number;
  minDurationMs: number;
  maxDurationMs: number;
  color: string;
};

export const RAIN_CONFIGS: Record<'RAIN' | 'THUNDERSTORM', RainConfig> = {
  RAIN: {
    streakCount: 30,
    minDurationMs: 600,
    maxDurationMs: 1000,
    color: 'rgba(200, 220, 255, 0.4)',
  },
  THUNDERSTORM: {
    streakCount: 60,
    minDurationMs: 400,
    maxDurationMs: 700,
    color: 'rgba(180, 200, 240, 0.5)',
  }
};
