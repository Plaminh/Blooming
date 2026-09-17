# Data Model

No new database tables are needed. The statistics feature relies entirely on aggregating existing persisted entities.

## Entities Read

1. **User Settings**: Used to determine the user's timezone if not provided by the client.
2. **FocusRun**: Used to compute total focus time and distinct study days.
   - Filters: `user_id = :user_id AND status = 'ENDED' AND started_at >= :start AND started_at < :end`
   - Data points: `actual_duration_seconds`, `started_at` AT TIME ZONE
3. **DailyPlan**: Used to compute plan outcomes and plan history.
   - Filters: `user_id = :user_id AND plan_date >= :start AND plan_date <= :end`
   - Classification: `status == 'COMPLETED'` vs `status IN ('CONFIRMED', 'ACTIVE')`
4. **PlanBlock**: Used to derive task completion counts per plan in Plan History.
   - Filters: `daily_plan_id = :plan_id AND block_type = 'TASK'`
