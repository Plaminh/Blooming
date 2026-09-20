"""Draft editor: deterministic commands first, budgeted LLM fallback second."""

from pydantic import BaseModel, Field, ValidationError

from app.ai.budget import BudgetMode, available_routes, get_budget_mode
from app.ai.editor_rules import parse_edit
from app.ai.patches import PatchOp, apply_patch
from app.ai.providers import LLMError, llm_provider
from app.core.config import settings
from app.schemas.assistant import ChatResponse
from app.schemas.drafts import TodayDraft
from app.schemas.today import TodayPreviewRequest
from app.services.today_service import today_service


class EditorOutput(BaseModel):
    ops: list[PatchOp] = Field(min_length=1, max_length=3)


async def edit(message: str, draft: TodayDraft, ctx, *, history: list[dict] | None = None) -> ChatResponse:
    ops = parse_edit(message, draft)
    tier = "RULES"
    mode = await get_budget_mode(ctx.db, ctx.user_id, "EDITOR", now=ctx.now)
    routes = ""
    if ops is None and mode == BudgetMode.NORMAL:
        routes = await available_routes(ctx.db, settings.AI_ROUTE_EDITOR, now=ctx.now)
    if ops is None and mode == BudgetMode.NORMAL and routes:
        await ctx.db.commit()
        try:
            raw = await llm_provider.call(
                routes,
                [{"role": "system", "content": "Return only safe patch operations for the supplied draft. Never save it."},
                 *(history or [])[-4:],
                 {"role": "user", "content": message + "\nDraft: " + draft.model_dump_json()}],
                temperature=0, max_tokens=500, require_json=True,
                json_schema=EditorOutput.model_json_schema(), db=ctx.db,
                user_id=ctx.user_id, purpose="EDITOR",
            )
            ops = EditorOutput.model_validate(raw).ops
            tier = "LLM"
        except (LLMError, ValidationError):
            ops = None
    if not ops:
        question = "Which task should I change, and what should change?"
        return ChatResponse(reply=question, question=question, intent="EDIT_DRAFT", tier="RULES",
                            draft=draft, degraded=mode.value if mode != BudgetMode.NORMAL else None)
    try:
        changed = apply_patch(draft, ops)
    except ValueError as exc:
        question = str(exc)
        return ChatResponse(reply=question, question=question, intent="EDIT_DRAFT", tier=tier, draft=draft)
    assert isinstance(changed, TodayDraft)
    preview = await today_service.preview_today_draft(
        ctx.db, ctx.user_id, TodayPreviewRequest(draft=changed)
    )
    return ChatResponse(
        reply="I updated the draft. Review the new preview before saving.",
        intent="EDIT_DRAFT",
        tier=tier,
        draft=changed,
        preview=preview.model_dump(mode="json"),
        degraded=mode.value if mode != BudgetMode.NORMAL else None,
    )
