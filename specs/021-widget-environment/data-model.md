# Asset Migration Data Model Mapping

This file defines the explicit structural mapping for the widget environmental assets, migrating them from the repository root to the Vite static asset hierarchy.

## Path Mapping

### Daytime Layer (Time-of-day backgrounds)
| Old Path | New Path | Action |
|----------|----------|--------|
| `/daytime/dawn.png` | `frontend/src/lib/assets/widget/environment/daytime/dawn.png` | Move |
| `/daytime/morning.png` | `frontend/src/lib/assets/widget/environment/daytime/morning.png` | Move |
| `/daytime/noon.png` | `frontend/src/lib/assets/widget/environment/daytime/noon.png` | Move |
| `/daytime/afternoon.png` | `frontend/src/lib/assets/widget/environment/daytime/afternoon.png` | Move |
| `/daytime/sunset.png` | `frontend/src/lib/assets/widget/environment/daytime/sunset.png` | Move |
| `/daytime/night.png` | `frontend/src/lib/assets/widget/environment/daytime/night.png` | Move |

### Season Layer (Vegetation/environment overlays)
| Old Path | New Path | Action |
|----------|----------|--------|
| `/season/spring.png` | `frontend/src/lib/assets/widget/environment/season/spring.png` | Move |
| `/season/summer.png` | `frontend/src/lib/assets/widget/environment/season/summer.png` | Move |
| `/season/autumn.png` | `frontend/src/lib/assets/widget/environment/season/autumn.png` | Move |
| `/season/winter.png` | `frontend/src/lib/assets/widget/environment/season/winter.png` | Move |

### Weather Layer (Static weather effects)
| Old Path | New Path | Action |
|----------|----------|--------|
| `/weather/cloudy.png` | `frontend/src/lib/assets/widget/environment/weather/cloudy.png` | Move |
| `/weather/overcast.png` | `frontend/src/lib/assets/widget/environment/weather/overcast.png` | Move |
| `/weather/thunder-storm.png` | `frontend/src/lib/assets/widget/environment/weather/storm-overlay.png` | Move & Rename |

## Composition Rule Constraints

- Assets must NOT be flattened or pre-composed.
- They must remain individual PNG files.
- The Widget Scene will layer them dynamically on the client side:
  1. `daytime/*` (Background)
  2. `season/*` (Foreground Vegetation)
  3. `weather/*` (Ambience Overlay)
  4. `RainLayer.svelte` (Procedural CSS Rain)

## TypeScript Environment Model

The environment types strictly constrain the available variants:

```typescript
export type Daytime = 'DAWN' | 'MORNING' | 'NOON' | 'AFTERNOON' | 'SUNSET' | 'NIGHT';
export type Season = 'SPRING' | 'SUMMER' | 'AUTUMN' | 'WINTER';
export type Weather = 'CLEAR' | 'CLOUDY' | 'OVERCAST' | 'RAIN' | 'THUNDERSTORM';
```
