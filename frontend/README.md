# Blooming desktop frontend

The intended desktop UI is **Svelte + TypeScript + Vite**, hosted by **Tauri 2**. Product decisions live in `../docs/02-product/Blooming-Concept-Updated.md`.

This folder currently still contains a leftover **Next.js / React** scaffold. That scaffold is not the product frontend. Do not treat Next.js routing, React components, or a web-only deployment as Blooming architecture.

## Product surfaces

| Surface | Role |
|---|---|
| Today | Planning chat, Task Draft, timeline, task selection, Pomodoro setup, re-planning |
| Goals | Goal, Roadmap, Milestone, Reminder actions |
| Settings | Account, timezone, focus defaults, widget behavior, quiet hours, Mr. Bloom name, PlantType, weather-context preferences |
| Mr. Bloom widget | Lightweight always-on-top window; WidgetState plus composed time/weather/plant layers |

The full application opens on Today. There is no Home screen, separate chat screen, or Garden screen.

## Widget rules

Functional WidgetState: `DEFAULT`, `REMINDER`, `FOCUSING`, `SESSION_RESULT`, `HIDDEN`.

Visual WidgetContext is independent from WidgetState: time-of-day (`MORNING`, `AFTERNOON`, `EVENING`, `NIGHT`) and optional WeatherContext (`CLEAR`, `CLOUDY`, `RAINY`, `STORMY`, `FOGGY`, `SNOWY`, `UNKNOWN`). The rendered widget composes WidgetState + WidgetContext + PlantType/GardenState. Do not ship a unique screen for every combination.

Time and weather must not affect scheduling, reminder timing, or Heart Progress. If weather-aware visuals are disabled, use time-only WidgetContext with no weather overlay. If weather is unavailable, WeatherContext may be `UNKNOWN` and presentation remains time-only.

## Plant presentation

Select artwork from PlantType (`POTHOS`, `CACTUS`, `BONSAI`, `SUNFLOWER`, `LOTUS`) plus the shared GardenState stage. Switching PlantType is visual only.

## Local development (current leftover scaffold)

Until the Svelte/Tauri tree replaces this folder, the existing Next.js commands only run the leftover scaffold and must not be cited as the product stack.

```bash
npm install
npm run dev
```

The product local loop is a Tauri desktop shell talking to the FastAPI backend, not a Vercel web deploy.
