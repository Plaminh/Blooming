import hashlib
import hmac
import logging
from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.errors import ResourceNotFoundError, UnauthorizedOwnershipError
from app.core.scheduler import DeterministicScheduler, ScheduleTask, ScheduleWindow
from app.core.time_utils import safe_timezone
from app.crud.crud_daily_plan import daily_plan as crud_daily_plan
from app.crud.crud_task import task as crud_task
from app.db.models.daily_plans import PlanBlock, PlanRevision
from app.db.models.planning import PlanningSession
from app.db.models.tasks import Task
from app.db.models.users import UserSettings
from app.schemas.today import (
    TodayBlock,
    TodayPreviewRequest,
    TodayPreviewResponse,
    TodaySaveRequest,
    TodayTaskEdit,
    TodayTaskStatusUpdate,
)

logger = logging.getLogger(__name__)
USABLE_PLAN_STATUSES = {"CONFIRMED", "ACTIVE", "COMPLETED"}


class TodayService:
    async def get_today(
        self, db: AsyncSession, user_id: UUID, local_date: date | None = None
    ) -> dict:
        settings = await db.scalar(select(UserSettings).where(UserSettings.user_id == user_id))
        tz = safe_timezone(settings.timezone if settings else "UTC")
        if local_date is None:
            local_date = datetime.now(tz).date()

        plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
        if not plan or plan.status not in USABLE_PLAN_STATUSES:
            return {"plan_date": local_date, "status": "NO_PLAN", "timezone": str(tz)}

        revision = await db.scalar(select(PlanRevision).where(PlanRevision.daily_plan_id == plan.id).order_by(PlanRevision.revision_number.desc()).limit(1))
        scheduling = revision.after_snapshot if revision else {}
        task_draft_map = scheduling.get("task_draft_map", {})
        blocks = sorted(plan.plan_blocks, key=lambda b: b.planned_start_at)

        block_dicts = []
        for b in blocks:
            b_dict = {
                "id": b.id,
                "block_type": b.block_type,
                "task_id": b.task_id,
                "draft_task_id": task_draft_map.get(str(b.task_id)) if b.task_id else None,
                "title": b.title,
                "planned_start_at": b.planned_start_at,
                "planned_end_at": b.planned_end_at,
                "position": b.position,
                "status": b.status,
                "is_locked": b.is_locked,
                "description": b.task.description if b.task else None,
                "category": b.task.category if b.task else None,
                "estimated_duration_minutes": b.task.estimated_duration_minutes
                if b.task
                else None,
            }
            block_dicts.append(b_dict)

        return {
            "plan_date": plan.plan_date,
            "status": plan.status,
            "reality_check": plan.reality_check,
            "blocks": block_dicts,
            "timezone": str(tz),
            "unscheduled_tasks": scheduling.get("unscheduled_tasks", []),
            "reasons": scheduling.get("reasons", []),
        }

    async def update_task_from_today(
        self, db: AsyncSession, user_id: UUID, task_id: UUID, obj_in: TodayTaskEdit
    ) -> Task:
        task_db = await crud_task.get_with_plan_blocks(db, id=task_id, user_id=user_id)
        if not task_db:
            raise ResourceNotFoundError("Task not found")
        if task_db.user_id != user_id:
            raise UnauthorizedOwnershipError()

        if obj_in.title is not None:
            task_db.title = obj_in.title
        if obj_in.estimated_duration_minutes is not None:
            task_db.estimated_duration_minutes = obj_in.estimated_duration_minutes
        if "description" in obj_in.model_fields_set:
            task_db.description = obj_in.description
        if "category" in obj_in.model_fields_set:
            task_db.category = obj_in.category

        db.add(task_db)

        # update title in plan blocks as well
        if obj_in.title is not None:
            for b in task_db.plan_blocks:
                b.title = obj_in.title
                db.add(b)

        await db.commit()
        return task_db

    async def update_task_status_from_today(
        self,
        db: AsyncSession,
        user_id: UUID,
        task_id: UUID,
        obj_in: TodayTaskStatusUpdate,
        commit: bool = True,
    ) -> Task:
        from app.db.models.users import User

        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        task_db = await crud_task.get_with_plan_blocks(db, id=task_id, user_id=user_id)
        if not task_db:
            raise ResourceNotFoundError("Task not found")
        if task_db.user_id != user_id:
            raise UnauthorizedOwnershipError()

        if task_db.status == obj_in.status:
            return task_db  # Idempotent

        task_db.status = obj_in.status
        if obj_in.status == "COMPLETED":
            task_db.completed_at = datetime.now(timezone.utc)

            from app.core.economy import LEAVES_PER_TASK
            from app.services.garden_service import award_resources

            # Award leaves
            await award_resources(
                db=db,
                user_id=user_id,
                resource_type="LEAVES",
                amount=LEAVES_PER_TASK,
                event_type="TASK_COMPLETED",
                idempotency_key=f"task_completed_{task_id}",
                source_id=task_id,
            )
        else:
            task_db.completed_at = None

        db.add(task_db)

        # update plan blocks
        block_status_map = {
            "DRAFT": "PLANNED",
            "PENDING": "PLANNED",
            "IN_PROGRESS": "ACTIVE",
            "COMPLETED": "COMPLETED",
            "SKIPPED": "SKIPPED",
            "CANCELLED": "CANCELLED",
        }
        b_status = block_status_map.get(obj_in.status, "PLANNED")

        for b in task_db.plan_blocks:
            b.status = b_status
            if obj_in.status == "COMPLETED":
                b.completed_at = task_db.completed_at
            else:
                b.completed_at = None
            db.add(b)

        await db.flush()
        if commit:
            await db.commit()
        return task_db

    async def replan_today(
        self, db: AsyncSession, user_id: UUID, commit: bool = True
    ) -> dict:
        from app.db.models.users import User

        await db.execute(select(User.id).where(User.id == user_id).with_for_update())
        settings = await db.scalar(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        now = datetime.now(timezone.utc)
        local_date = now.astimezone(
            safe_timezone(settings.timezone if settings else "UTC")
        ).date()
        plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
        if not plan or plan.status not in USABLE_PLAN_STATUSES:
            return {"plan_date": local_date, "status": "NO_PLAN"}
        await db.refresh(plan, ["plan_blocks", "availability_windows"])
        blocks = list(plan.plan_blocks)
        previous = await db.scalar(select(PlanRevision).where(PlanRevision.daily_plan_id == plan.id).order_by(PlanRevision.revision_number.desc()).limit(1))
        pending_ids = {UUID(tid) for tid in previous.after_snapshot.get("unscheduled_tasks", [])} if previous else set()
        task_ids = {b.task_id for b in blocks if b.task_id} | pending_ids
        tasks = {
            t.id: t
            for t in (
                await db.scalars(
                    select(Task)
                    .options(selectinload(Task.dependencies))
                    .where(Task.id.in_(task_ids), Task.user_id == user_id)
                )
            ).all()
        }
        from app.db.models.focus import FocusRun
        active_task_ids = set((await db.scalars(select(FocusRun.task_id).where(FocusRun.user_id == user_id, FocusRun.status.in_(("READY", "FOCUSING", "PAUSED"))))).all())
        preserved, eligible = [], []
        for block in blocks:
            task = tasks.get(block.task_id)
            terminal = block.status in ("COMPLETED", "SKIPPED", "CANCELLED") or (task and task.status in ("COMPLETED", "SKIPPED", "CANCELLED"))
            fixed_remaining = block.planned_end_at > now and (block.is_locked or block.status == "ACTIVE" or block.task_id in active_task_ids or block.block_type == "FIXED_EVENT" or (task and task.scheduling_type == "FIXED"))
            if terminal or fixed_remaining:
                preserved.append(block)
            else:
                eligible.append(block)

        # Subtract reservations even when they straddle now or an availability boundary.
        windows = [
            ScheduleWindow(max(w.available_start_at, now), w.available_end_at)
            for w in plan.availability_windows
            if w.available_end_at > now
        ]
        for block in preserved:
            if block.status in ("COMPLETED", "SKIPPED", "CANCELLED") or (tasks.get(block.task_id) and tasks[block.task_id].status in ("COMPLETED", "SKIPPED", "CANCELLED")):
                continue
            gaps = []
            for window in windows:
                if (
                    block.planned_end_at <= window.start_at
                    or block.planned_start_at >= window.end_at
                ):
                    gaps.append(window)
                else:
                    if window.start_at < block.planned_start_at:
                        gaps.append(
                            ScheduleWindow(window.start_at, block.planned_start_at)
                        )
                    if block.planned_end_at < window.end_at:
                        gaps.append(ScheduleWindow(block.planned_end_at, window.end_at))
            windows = gaps

        completed_ids = set(
            (
                await db.scalars(
                    select(Task.id).where(
                        Task.user_id == user_id, Task.status == "COMPLETED"
                    )
                )
            ).all()
        )
        schedule_tasks = []
        candidate_ids = {b.task_id for b in eligible if b.task_id} | pending_ids
        for task_id in sorted(candidate_ids, key=str):
            task = tasks.get(task_id)
            if not task or task.status not in ("DRAFT", "PENDING", "IN_PROGRESS"):
                continue
            reserved_minutes = sum(
                max(0, int((b.planned_end_at - (b.planned_start_at if b.status == "COMPLETED" else max(b.planned_start_at, now))).total_seconds() // 60))
                for b in preserved
                if b.task_id == task_id
            )
            remaining_minutes = max(
                0, task.estimated_duration_minutes - reserved_minutes
            )
            if remaining_minutes == 0:
                continue
            schedule_tasks.append(
                ScheduleTask(
                    id=task.id,
                    title=task.title,
                    estimated_duration_minutes=remaining_minutes,
                    priority=task.priority,
                    scheduling_type="FLEXIBLE",
                    created_at=task.created_at,
                    is_splittable=task.is_splittable,
                    min_split_duration_minutes=task.min_split_duration_minutes,
                    preferred_break_duration_minutes=task.preferred_break_duration_minutes,
                    dependencies=[
                        d.depends_on_task_id
                        for d in task.dependencies
                        if d.depends_on_task_id not in completed_ids
                    ],
                )
            )
        reserved_ends = {}
        for block in preserved:
            if block.task_id and block.task_id not in completed_ids and block.planned_end_at > now and block.status not in ("SKIPPED", "CANCELLED"):
                reserved_ends[block.task_id] = max(reserved_ends.get(block.task_id, now), block.planned_end_at)
        result = DeterministicScheduler().schedule(schedule_tasks, windows, satisfied_dependencies=reserved_ends)
        for block in eligible:
            await db.delete(block)
        await db.flush()
        # Preserve historical rows, including their positions; new rows receive unused positions.
        position = max((b.position for b in preserved), default=-1) + 1
        for offset, block in enumerate(result.blocks):
            db.add(
                PlanBlock(
                    daily_plan_id=plan.id,
                    task_id=block.task_id,
                    block_type=block.block_type,
                    title=block.title,
                    planned_start_at=block.start_at,
                    planned_end_at=block.end_at,
                    position=position + offset,
                    status="PLANNED",
                    created_by="SCHEDULER",
                )
            )
        plan.reality_check = "OVERLOADED" if result.unscheduled_tasks else ("COMFORTABLE" if result.workload_minutes <= result.available_minutes * 0.8 else "TIGHT")
        db.add(PlanRevision(daily_plan_id=plan.id, revision_number=(previous.revision_number if previous else 0) + 1, reason="Replan unfinished work", trigger_type="RECOVERY", generated_by="SYSTEM", before_snapshot={"block_ids": [str(b.id) for b in blocks]}, after_snapshot=jsonable_encoder({"unscheduled_tasks": result.unscheduled_tasks, "reasons": result.reasons})))
        await db.flush()
        await db.refresh(plan, ["plan_blocks"])
        if commit:
            await db.commit()
        logger.info("replan_result", extra={"unscheduled_count": len(result.unscheduled_tasks), "scheduled_count": len(result.blocks), "committed": commit})
        return await self.get_today(db, user_id, local_date)



    
    
    def _generate_hmac_token(self, user_id: UUID, draft_json: str) -> str:
        import base64
        import json
        import time
        
        secret = settings.SECRET_KEY.get_secret_value().encode()
        expiry = int(time.time()) + 3600 * 24 # 24 hours
        purpose = "today_preview"
        
        msg = f"{user_id}:{purpose}:{expiry}:{draft_json}".encode()
        signature = hmac.new(secret, msg, hashlib.sha256).hexdigest()
        
        token_data = {"exp": expiry, "sig": signature}
        return base64.urlsafe_b64encode(json.dumps(token_data).encode()).decode()

    def _verify_hmac_token(self, user_id: UUID, draft_json: str, token: str) -> bool:
        import base64
        import json
        import time
        
        try:
            token_data = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
            expiry = token_data["exp"]
            signature = token_data["sig"]
        except Exception:
            return False
            
        if time.time() > expiry:
            return False
            
        secret = settings.SECRET_KEY.get_secret_value().encode()
        purpose = "today_preview"
        msg = f"{user_id}:{purpose}:{expiry}:{draft_json}".encode()
        expected = hmac.new(secret, msg, hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(expected, signature)

    def _normalize_dt(self, dt, tz):
        from datetime import date, datetime, time
        if not isinstance(dt, date) and not isinstance(dt, datetime):
            return dt
        if not isinstance(dt, datetime):
            # date-only, end-of-day rule
            dt = datetime.combine(dt, time(23, 59, 59))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=tz)
        return dt.astimezone(tz)

    def _normalize_and_schedule(self, draft, tz, local_date, user_id):
        import uuid
        from datetime import datetime, timedelta

        from app.core.scheduler import (
            DeterministicScheduler,
            ScheduleTask,
            ScheduleWindow,
        )
        
        windows = []
        for w in draft.windows:
            start_dt = datetime.strptime(w.start, "%H:%M").replace(year=local_date.year, month=local_date.month, day=local_date.day, tzinfo=tz)
            end_dt = datetime.strptime(w.end, "%H:%M").replace(year=local_date.year, month=local_date.month, day=local_date.day, tzinfo=tz)
            windows.append(ScheduleWindow(start_at=start_dt, end_at=end_dt))
        
        tasks = []
        # Generate deterministic UUIDs from user_id and draft task ID
        draft_to_uuid = {t.id: uuid.uuid5(user_id, t.id) for t in draft.tasks}
        
        base_time = datetime(2000, 1, 1, tzinfo=tz)
        for i, t in enumerate(draft.tasks):
            sched_priority = t.priority
            if sched_priority not in ("URGENT", "HIGH", "MEDIUM", "LOW"):
                sched_priority = "MEDIUM"
                
            tasks.append(ScheduleTask(
                id=draft_to_uuid[t.id],
                title=t.title,
                estimated_duration_minutes=t.durationMin,
                priority=sched_priority,
                scheduling_type=t.schedulingType,
                created_at=base_time + timedelta(seconds=i),
                is_splittable=t.splittable,
                fixed_start_at=self._normalize_dt(t.fixedStart, tz) if t.fixedStart else None,
                fixed_end_at=self._normalize_dt(t.fixedEnd, tz) if t.fixedEnd else None,
                dependencies=[draft_to_uuid[d] for d in t.dependencies if d in draft_to_uuid]
            ))
            
        result = DeterministicScheduler().schedule(tasks, windows)
        if any(reason["code"] == "FIXED_TASK_OVERLAP" for reason in result.reasons):
            from fastapi import HTTPException

            raise HTTPException(status_code=422, detail="Fixed tasks overlap.")
        reality_check = "OVERLOADED" if result.unscheduled_tasks else ("COMFORTABLE" if result.workload_minutes <= result.available_minutes * 0.8 else "TIGHT")
        
        return result, reality_check, draft_to_uuid

    async def preview_today_draft(self, db: AsyncSession, user_id: UUID, request: TodayPreviewRequest) -> TodayPreviewResponse:
        from fastapi import HTTPException

        from app.db.models.users import UserSettings
        
        user_settings = await db.scalar(select(UserSettings).where(UserSettings.user_id == user_id))
        user_tz = safe_timezone(user_settings.timezone if user_settings else "UTC")
        
        if request.draft.timezone != str(user_tz):
            raise HTTPException(status_code=422, detail="Draft timezone must match user timezone exactly.")
            
        tz = user_tz
        current_local_date = datetime.now(tz).date()
        local_date = request.draft.planDate
        
        if local_date < current_local_date:
            raise HTTPException(status_code=422, detail="Cannot plan for a past date.")
            
        result, reality_check, draft_to_uuid = self._normalize_and_schedule(request.draft, tz, local_date, user_id)
        uuid_to_draft = {v: k for k, v in draft_to_uuid.items()}
        
        blocks = []
        for i, b in enumerate(result.blocks):
            blocks.append(TodayBlock(
                id=uuid4(),
                block_type="TASK" if b.task_id and b.block_type == "FIXED_EVENT" else b.block_type,
                task_id=b.task_id, 
                title=b.title,
                planned_start_at=b.start_at,
                planned_end_at=b.end_at,
                position=i,
                status="PLANNED",
                is_locked=False,
                draft_task_id=uuid_to_draft.get(b.task_id) if b.task_id else None
            ))
            
        unscheduled = []
        for ut_id in result.unscheduled_tasks:
            draft_tid = uuid_to_draft.get(ut_id) if ut_id else None
            title = None
            if draft_tid:
                for t in request.draft.tasks:
                    if t.id == draft_tid:
                        title = t.title
                        break
            
            reason_code = None
            for r in result.reasons:
                if r.get('task_id') == ut_id:
                    reason_code = r.get('code')
                    break
                    
            from app.schemas.today import UnscheduledTaskInfo
            unscheduled.append(UnscheduledTaskInfo(
                draft_task_id=draft_tid,
                reason=reason_code,
                title=title
            ))
            
        draft_json = request.draft.model_dump_json()
        token = self._generate_hmac_token(user_id, draft_json)
            
        return TodayPreviewResponse(
            plan_date=local_date,
            timezone=str(tz),
            preview_token=token,
            reality_check=reality_check,
            blocks=blocks,
            unscheduled_tasks=unscheduled,
            reasons=result.reasons
        )

    async def save_today_draft(self, db: AsyncSession, user_id: UUID, request: TodaySaveRequest) -> dict:
        import hashlib

        from fastapi import HTTPException

        from app.db.models.daily_plans import DailyPlan, PlanBlock, PlanRevision
        from app.db.models.tasks import Task, TaskDependency
        from app.db.models.users import UserSettings
        
        draft_json = request.draft.model_dump_json()
        if not self._verify_hmac_token(user_id, draft_json, request.preview_token):
            raise HTTPException(status_code=409, detail="Draft has changed since last preview. Please preview again.")
            
        draft_hash = hashlib.sha256(draft_json.encode()).hexdigest()
        
        if request.session_id:
            session = await db.scalar(select(PlanningSession).where(PlanningSession.id == request.session_id))
            if not session:
                raise HTTPException(status_code=404, detail="Planning session not found")
            if session.user_id != user_id:
                raise HTTPException(status_code=403, detail="Unauthorized")
            if session.status != "OPEN":
                raise HTTPException(status_code=409, detail="Session is not open for saving")
        
        user_settings = await db.scalar(select(UserSettings).where(UserSettings.user_id == user_id))
        user_tz = safe_timezone(user_settings.timezone if user_settings else "UTC")
        if request.draft.timezone != str(user_tz):
            raise HTTPException(status_code=422, detail="Draft timezone must match user timezone exactly.")
            
        tz = user_tz
        current_local_date = datetime.now(tz).date()
        local_date = request.draft.planDate
        if local_date < current_local_date:
            raise HTTPException(status_code=422, detail="Cannot plan for a past date.")

        result, reality_check, draft_to_uuid = self._normalize_and_schedule(request.draft, tz, local_date, user_id)
        uuid_to_draft = {v: k for k, v in draft_to_uuid.items()}
        
        existing_plan = await crud_daily_plan.get_by_date(db, user_id, local_date)
        
        # Idempotency Check
        if existing_plan:
            revision = await db.scalar(select(PlanRevision).where(PlanRevision.daily_plan_id == existing_plan.id).order_by(PlanRevision.revision_number.desc()).limit(1))
            if revision and revision.after_snapshot.get("draft_hash") == draft_hash:
                return await self.get_today(db, user_id, local_date)
                
            # Delete old blocks explicitly
            blocks_result = await db.execute(select(PlanBlock).where(PlanBlock.daily_plan_id == existing_plan.id))
            for block in blocks_result.scalars():
                await db.delete(block)

            # Delete AI tasks from previous save if not completed
            if revision and "created_task_ids" in revision.after_snapshot:
                prev_task_ids_str = revision.after_snapshot["created_task_ids"]
                if prev_task_ids_str:
                    from uuid import UUID
                    prev_task_ids = [UUID(pid) if isinstance(pid, str) else pid for pid in prev_task_ids_str]
                    tasks_res = await db.execute(select(Task).where(Task.id.in_(prev_task_ids)))
                    for t in tasks_res.scalars():
                        if t.status != "COMPLETED":
                            deps_res = await db.execute(select(TaskDependency).where(
                                (TaskDependency.task_id == t.id) | 
                                (TaskDependency.depends_on_task_id == t.id)
                            ))
                            for dep in deps_res.scalars():
                                await db.delete(dep)
                            await db.delete(t)
            
            existing_plan.reality_check = reality_check
            existing_plan.timezone_snapshot = str(tz)
            if request.session_id:
                existing_plan.planning_session_id = request.session_id
            plan = existing_plan
        else:
            revision = None
            plan = DailyPlan(
                user_id=user_id,
                plan_date=local_date,
                status="ACTIVE",
                confirmed_at=datetime.now(timezone.utc),
                planning_session_id=request.session_id,
                reality_check=reality_check,
                timezone_snapshot=str(tz)
            )
            db.add(plan)
            
        await db.flush()
            
        task_id_map = {}
        new_tasks = []
        for t_draft in request.draft.tasks:
            new_task = Task(
                user_id=user_id,
                title=t_draft.title,
                estimated_duration_minutes=t_draft.durationMin,
                priority=t_draft.priority,
                scheduling_type=t_draft.schedulingType,
                importance="CORE" if t_draft.priority in ("URGENT", "HIGH") else "OPTIONAL",
                deadline_at=self._normalize_dt(t_draft.deadline, tz) if t_draft.deadline else None,
                fixed_start_at=self._normalize_dt(t_draft.fixedStart, tz) if t_draft.fixedStart else None,
                fixed_end_at=self._normalize_dt(t_draft.fixedEnd, tz) if t_draft.fixedEnd else None,
                is_splittable=t_draft.splittable,
                source="AI"
            )
            db.add(new_task)
            new_tasks.append((t_draft, new_task))
            
        await db.flush()
        
        for t_draft, new_task in new_tasks:
            task_id_map[t_draft.id] = new_task.id
            
        for t_draft, new_task in new_tasks:
            for dep_draft_id in t_draft.dependencies:
                if dep_draft_id in task_id_map:
                    db.add(TaskDependency(task_id=new_task.id, depends_on_task_id=task_id_map[dep_draft_id]))

        await db.flush()
        
        unscheduled = []
        for ut_id in result.unscheduled_tasks:
            draft_tid = uuid_to_draft.get(ut_id) if ut_id else None
            title = None
            if draft_tid:
                for t in request.draft.tasks:
                    if t.id == draft_tid:
                        title = t.title
                        break
            
            reason_code = None
            for r in result.reasons:
                if r.get('task_id') == ut_id:
                    reason_code = r.get('code')
                    break
                    
            from app.schemas.today import UnscheduledTaskInfo
            unscheduled.append(UnscheduledTaskInfo(
                draft_task_id=draft_tid,
                reason=reason_code,
                title=title
            ))
            
        blocks_created = []
        for idx, block_item in enumerate(result.blocks):
            t_id = None
            if block_item.task_id:
                draft_task_id = uuid_to_draft.get(block_item.task_id)
                t_id = task_id_map.get(draft_task_id)
            
            block = PlanBlock(
                daily_plan_id=plan.id,
                block_type="TASK" if t_id and block_item.block_type == "FIXED_EVENT" else block_item.block_type,
                planned_start_at=block_item.start_at,
                planned_end_at=block_item.end_at,
                task_id=t_id,
                title=block_item.title,
                position=idx,
                is_locked=False
            )
            db.add(block)
            blocks_created.append(block)
            
        last_rev = await db.scalar(select(func.max(PlanRevision.revision_number)).where(PlanRevision.daily_plan_id == plan.id))
        rev_num = (last_rev or 0) + 1
        
        created_task_ids = [str(new_task.id) for _, new_task in new_tasks]
        task_draft_map = {str(new_task.id): t_draft.id for t_draft, new_task in new_tasks}
        
        rev = PlanRevision(
            daily_plan_id=plan.id,
            revision_number=rev_num,
            reason="AI_DRAFT_APPLIED",
            trigger_type="MANUAL_EDIT",
            generated_by="AI",
            before_snapshot={},
            after_snapshot={
                "blocks": len(blocks_created),
                "draft_hash": draft_hash,
                "created_task_ids": created_task_ids,
                "task_draft_map": task_draft_map,
                "unscheduled_tasks": [u.model_dump(mode="json") for u in unscheduled],
                "reasons": jsonable_encoder(result.reasons)
            }
        )
        db.add(rev)
        
        await db.commit()

        db.expire(plan, ["plan_blocks"])
        return await self.get_today(db, user_id, local_date)



today_service = TodayService()
