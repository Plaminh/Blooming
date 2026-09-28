from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.plans.today_query import (
    _pending_task_infos,
    _get_plan_for_preview_validation,
    get_today_draft,
    get_today,
)
from app.services.plans.draft_preview import (
    _normalize_dt,
    _normalize_and_schedule,
    preview_today_draft,
)
from app.services.plans.draft_save import (
    _reusable_task,
    _owned_template_id,
    _materialize_task,
    save_today_draft,
)
from app.services.plans.replan import replan_today
from app.services.plans.task_status import (
    sync_daily_plan_completion,
    update_task_from_today,
    update_task_status_from_today,
)


class TodayService:
    _pending_task_infos = staticmethod(_pending_task_infos)
    sync_daily_plan_completion = staticmethod(sync_daily_plan_completion)
    _reusable_task = staticmethod(_reusable_task)
    _owned_template_id = staticmethod(_owned_template_id)
    _materialize_task = staticmethod(_materialize_task)
    _get_plan_for_preview_validation = staticmethod(_get_plan_for_preview_validation)
    get_today_draft = staticmethod(get_today_draft)
    get_today = staticmethod(get_today)
    update_task_from_today = staticmethod(update_task_from_today)
    update_task_status_from_today = staticmethod(update_task_status_from_today)
    replan_today = staticmethod(replan_today)
    _normalize_dt = staticmethod(_normalize_dt)
    _normalize_and_schedule = staticmethod(_normalize_and_schedule)
    preview_today_draft = staticmethod(preview_today_draft)
    save_today_draft = staticmethod(save_today_draft)

    @staticmethod
    def _generate_hmac_token(
        user_id: UUID, draft_json: str, plan_version: str | None = None
    ) -> str:
        from app.core.preview_token import generate_hmac_token

        return generate_hmac_token(user_id, draft_json, plan_version)

    @staticmethod
    def _preview_token_claims(
        user_id: UUID, draft_json: str, token: str
    ) -> dict[str, str | int] | None:
        from app.core.preview_token import preview_token_claims

        return preview_token_claims(user_id, draft_json, token)

    @staticmethod
    def _verify_hmac_token(user_id: UUID, draft_json: str, token: str) -> bool:
        from app.core.preview_token import verify_hmac_token

        return verify_hmac_token(user_id, draft_json, token)

    @staticmethod
    async def _plan_version(db: AsyncSession, plan_id: UUID | None) -> str:
        from app.core.preview_token import plan_version

        return await plan_version(db, plan_id)


today_service = TodayService()
