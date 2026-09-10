# Use-Case Model

## Actors

| Actor | Role |
|---|---|
| User | Authenticates, plans in the full application, focuses, recovers, manages goals, acts on reminders, switches PlantType, and configures widget/weather settings. |
| LLM provider | Returns untrusted semantic interpretation and draft data for full-application planning chat. |
| Weather provider | Returns coarse current conditions used only for WeatherContext presentation. |
| System clock | Supplies trusted timer, local reminder due-time evaluation, and time-of-day context. |

## MVP use cases

| ID | Use case | Goal |
|---|---|---|
| UC-USER-01 | Manage account and settings | Authenticate and set timezone, focus defaults, quiet hours, widget behavior, PlantType, and weather-context preferences. |
| UC-PLAN-01 | Create Daily Plan | Turn a Task Draft into a realistic, reviewable Daily Plan timeline. |
| UC-PLAN-02 | Handle Overloaded Plan | Choose a feasible alternative without silent compression. |
| UC-AI-01 | Plan with Mr. Bloom | Convert natural language in the full application into a reviewable plan or roadmap draft. |
| UC-FOCUS-01 | Execute FocusRun | Start from Today, run Pomodoro, and record a canonical outcome. |
| UC-REPLAN-01 | Recover Remaining Day | Adapt flexible future work without changing protected history. |
| UC-GOAL-01 | Manage Goal Roadmap | Create/edit Goals and Milestones, including downstream-date warnings. |
| UC-REM-01 | Act on Milestone Reminder | Confirm a Daily Plan, complete, move, or defer a milestone from the widget or Goals. |
| UC-WIDGET-01 | Follow Plan on Widget | Use WidgetState `DEFAULT`, `REMINDER`, `FOCUSING`, `SESSION_RESULT`, and `HIDDEN` without free-form chat. |
| UC-PLANT-01 | Grow Garden and Switch Plant | Earn Heart Progress into one GardenState and change PlantType without resetting progress. |
| UC-WX-01 | Apply Weather Presentation | Optionally show WeatherContext ambience, falling back to time-of-day when weather is unavailable. |

The LLM provider never schedules, persists state, executes reminders, calculates Heart Progress, or chooses WeatherContext gameplay effects. The weather provider never affects planning, reminder timing, or Heart Progress. There is no email-reminder actor in the MVP.
