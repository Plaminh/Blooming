# Use-Case Model

## Actors

| Actor | Role |
|---|---|
| User | Authenticates, plans, focuses, recovers, manages goals, acts on reminders, and configures rest/settings. |
| LLM provider | Returns untrusted semantic interpretation and draft data. |
| Email provider | Delivers the basic milestone reminder. |
| System clock | Runs trusted timer, reminder, Water Reserve, and Rest Mode boundaries. |

## MVP use cases

| ID | Use case | Goal |
|---|---|---|
| UC-USER-01 | Manage account and settings | Authenticate and set user-local preferences/Rest Mode. |
| UC-PLAN-01 | Create Quick Plan | Turn a Task Draft into a realistic, reviewable timeline. |
| UC-PLAN-02 | Handle Overloaded Plan | Choose a feasible alternative without silent compression. |
| UC-AI-01 | Plan with Mr. Bloom | Convert natural language into a reviewable plan or roadmap draft. |
| UC-FOCUS-01 | Execute FocusRun | Focus, pause/resume, and record a canonical outcome. |
| UC-REPLAN-01 | Recover Remaining Day | Adapt flexible future work without changing protected history. |
| UC-GOAL-01 | Manage Goal Roadmap | Create/edit goals and milestones, including downstream-date warnings. |
| UC-REM-01 | Act on Milestone Reminder | Create tomorrow's plan, complete, move, or defer a milestone. |
| UC-PLANT-01 | Sustain Plant / Rest | Receive meaningful activity effects, manage Water Reserve, and use Rest Mode. |

The LLM provider never schedules, persists state, executes reminders, or calculates plant state. The email provider is limited to authenticated, idempotent notification delivery.
