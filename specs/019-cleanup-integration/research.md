# Corrective audit findings

The existing TodayService.replan_today method exists; its original implementation had block-preservation, reservation and position issues. The correct routes are PATCH /api/v1/today/tasks/{task_id} and POST /api/v1/today/replan (no body).

The two feature migrations changed unrelated currency/table structures and are removed. Authoritative SQL CREATE TABLE files receive only category, growth_points and milestone_reminder_lead_time_minutes plus constraints. The Alembic baseline remains untouched. Direct SQL updates require a manual update or recreation of existing local databases.

## Inspected sprite evidence

Visually inspected all five actual files under `frontend/static/assets/widget/plants/`: 2304x896, 8 columns, 2 rows, 288x448 cells. Indices are row-major, zero-based. Frame 0 is a seed, frame 1 a sprout, frame 4 a developed plant. Frames 12-15 show progressively stressed/wilted/dead plants, not advanced growth.

| Species | SPROUTING | GROWING | BLOOMING | FLOURISHING |
| --- | --- | --- | --- | --- |
| monstera | 1 | 4 | 7 | 10 |
| sunflower | 1 | 4 | 7 | 11 |
| bonsai | 1 | 4 | 10 | 11 |
| jasmine | 1 | 4 | 7 | 11 |
| lavender | 1 | 4 | 7 | 11 |

Monstera's bloom presentation is full foliage; bonsai flowers appear in frame 10. Vitality >=75 uses the healthy stage frame; 50-74 uses 12, 25-49 uses 13, 1-24 uses 14, zero uses 15. Atlases lack stressed juvenile variants, so decline uses the available mature variants. These are presentation tiers, not backend growth thresholds.

Backend growth_stage thresholds: SPROUTING 0-99, GROWING 100-299, BLOOMING 300-699, FLOURISHING 700+. Growth accompanies Leaves with original completion keys; no separate currency event. Persisted legacy stage is unchanged.

Quiet hours use the enabled flag and UserSettings timezone, including overnight ranges. Reminder original_due_at is the real deadline; delivery is deadline minus 0-43200 minutes (default 1440).

The red-dot 32x32 PNG was visually inspected and is a valid leaf icon with red dot. Rust references it and both tray assets are bundled. Application-root HTTP polling remains; native behavior requires separate runtime verification.

No new automated feature coverage is added. Historical tests remain, with minimal SettingsState adaptations for the intentional numeric reminder field. See quickstart.md for actual results and remaining manual checks.
